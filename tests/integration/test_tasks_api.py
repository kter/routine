"""Integration tests for Tasks API - CRUD E2E."""

import pytest
from fastapi.testclient import TestClient


TASK_PAYLOAD = {
    "title": "月次セキュリティパッチ確認",
    "description": "毎月のセキュリティパッチを確認する",
    "cronExpression": "0 10 1 * *",
    "timezone": "Asia/Tokyo",
    "estimatedMinutes": 60,
    "tags": ["security", "monthly"],
    "steps": [
        {
            "position": 1,
            "title": "パッチ一覧確認",
            "instruction": "AWS console でパッチ一覧を確認する",
            "evidenceType": "text",
            "isRequired": True,
        },
        {
            "position": 2,
            "title": "スクリーンショット取得",
            "instruction": "完了画面のスクリーンショットを取得する",
            "evidenceType": "image",
            "isRequired": False,
        },
    ],
}


class TestCreateTask:
    def test_creates_task_successfully(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "テストタスク",
                "cron_expression": "0 10 * * *",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "テストタスク"
        assert data["cron_expression"] == "0 10 * * *"
        assert "id" in data

    def test_creates_task_with_steps(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "ステップ付きタスク",
                "cron_expression": "0 10 1 * *",
                "steps": [
                    {"position": 1, "title": "ステップ1", "evidence_type": "text"},
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["steps"]) == 1
        assert data["steps"][0]["title"] == "ステップ1"

    def test_returns_422_for_invalid_cron(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/tasks",
            json={"title": "Bad cron", "cron_expression": "not-valid"},
        )
        assert resp.status_code == 422

    def test_returns_422_for_missing_title(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/tasks",
            json={"cron_expression": "0 10 * * *"},
        )
        assert resp.status_code == 422


class TestListTasks:
    def test_returns_empty_list_initially(self, client: TestClient) -> None:
        resp = client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_created_tasks(self, client: TestClient) -> None:
        client.post("/api/v1/tasks", json={"title": "T1", "cron_expression": "0 10 * * *"})
        client.post("/api/v1/tasks", json={"title": "T2", "cron_expression": "0 10 * * 1"})

        resp = client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetTask:
    def test_gets_existing_task(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "詳細タスク", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_returns_404_for_missing_task(self, client: TestClient) -> None:
        resp = client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000999")
        assert resp.status_code == 404


class TestUpdateTask:
    def test_updates_task_title(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "旧タイトル", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"title": "新タイトル"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "新タイトル"

    def test_updates_active_status(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "Active Task", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False


class TestDeleteTask:
    def test_deletes_existing_task(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "削除タスク", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 204

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_returns_404_for_missing_task(self, client: TestClient) -> None:
        resp = client.delete("/api/v1/tasks/00000000-0000-0000-0000-000000000999")
        assert resp.status_code == 404
