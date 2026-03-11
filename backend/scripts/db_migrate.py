from __future__ import annotations

import os
from pathlib import Path

import boto3
import psycopg2


def _find_cluster_endpoint(environment: str, region: str) -> str:
    client = boto3.client("dsql", region_name=region)
    expected_name = f"routineops-{environment}"

    paginator = client.get_paginator("list_clusters")
    for page in paginator.paginate():
        for cluster in page.get("clusters", []):
            details = client.get_cluster(identifier=cluster["identifier"])
            tags = details.get("tags", {})
            if tags.get("Environment") == environment and tags.get("Name") == expected_name:
                endpoint = details.get("endpoint")
                if endpoint:
                    return endpoint

    raise RuntimeError(f"Could not find DSQL cluster for ENV={environment}")


def _get_cluster_endpoint() -> str:
    endpoint = os.getenv("DB_CLUSTER_ENDPOINT")
    if endpoint:
        return endpoint

    environment = os.getenv("ENV", "dev")
    region = os.getenv("AWS_REGION", "ap-northeast-1")
    return _find_cluster_endpoint(environment, region)


def _iter_sql_statements(sql_path: Path) -> list[str]:
    lines = [
        line
        for line in sql_path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("--")
    ]
    sql = "\n".join(lines)
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def main() -> None:
    endpoint = _get_cluster_endpoint()
    region = os.getenv("AWS_REGION", "ap-northeast-1")
    token = boto3.client("dsql", region_name=region).generate_db_connect_admin_auth_token(
        Hostname=endpoint,
        Region=region,
    )

    repo_root = Path(__file__).resolve().parents[2]
    sql_files = sorted((repo_root / "db" / "schema").glob("*.sql")) + sorted(
        (repo_root / "db" / "indexes").glob("*.sql")
    )

    conn = psycopg2.connect(
        host=endpoint,
        port=5432,
        user="admin",
        password=token,
        dbname=os.getenv("DB_NAME", "postgres"),
        sslmode="require",
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            for sql_file in sql_files:
                for statement in _iter_sql_statements(sql_file):
                    cur.execute(statement)

            cur.execute("select tablename from pg_tables where schemaname='public' order by tablename")
            print(cur.fetchall())
    finally:
        conn.close()


if __name__ == "__main__":
    main()
