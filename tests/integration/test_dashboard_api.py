"""Integration tests for Dashboard API."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from routineops.infrastructure.db.models.task_model import TaskModel
from tests.integration.conftest import ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB


def assert_dashboard_item_contract(item: dict) -> None:
    assert set(item) == {
        "task_id",
        "title",
        "scheduled_for",
        "estimated_minutes",
        "execution_id",
        "status",
    }
    UUID(item["task_id"])
    assert isinstance(item["title"], str)
    assert isinstance(item["scheduled_for"], str)
    assert isinstance(item["estimated_minutes"], int)
    if item["execution_id"] is not None:
        UUID(item["execution_id"])
    if item["status"] is not None:
        assert isinstance(item["status"], str)


class TestDashboardApi:
    def test_returns_empty_dashboard_with_no_tasks(self, client: TestClient) -> None:
        resp = client.get("/api/v1/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "today" in data
        assert "overdue" in data
        assert "upcoming" in data
        assert data["today"] == []
        assert data["overdue"] == []
        assert data["upcoming"] == []

    def test_dashboard_includes_active_tasks(self, client: TestClient) -> None:
        # Create a daily task (should appear in today or upcoming)
        client.post(
            "/api/v1/tasks",
            json={"title": "日次タスク", "cron_expression": "0 10 * * *"},
        )

        resp = client.get("/api/v1/dashboard")
        assert resp.status_code == 200
        data = resp.json()

        all_items = data["today"] + data["upcoming"]
        for item in all_items:
            assert_dashboard_item_contract(item)
        titles = [item["title"] for item in all_items]
        assert "日次タスク" in titles

    def test_dashboard_excludes_inactive_tasks(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={"title": "無効タスク", "cron_expression": "0 10 * * *"},
        )
        task_id = create_resp.json()["id"]

        # Deactivate
        client.patch(f"/api/v1/tasks/{task_id}", json={"is_active": False})

        resp = client.get("/api/v1/dashboard")
        data = resp.json()

        all_items = data["today"] + data["overdue"] + data["upcoming"]
        titles = [item["title"] for item in all_items]
        assert "無効タスク" not in titles

    def test_dashboard_tolerates_invalid_timezone_data(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={"title": "不正timezoneタスク", "cron_expression": "0 10 * * *"},
        )
        task_id = UUID(create_resp.json()["id"])

        task = db_session.query(TaskModel).filter(TaskModel.id == task_id).one()
        task.timezone = ""
        db_session.commit()

        resp = client.get("/api/v1/dashboard")

        assert resp.status_code == 200
        data = resp.json()
        all_items = data["today"] + data["overdue"] + data["upcoming"]
        for item in all_items:
            assert_dashboard_item_contract(item)
        titles = [item["title"] for item in all_items]
        assert "不正timezoneタスク" in titles

    def test_dashboard_includes_execution_id_and_status_for_matching_execution(
        self,
        client: TestClient,
    ) -> None:
        scheduled_for = (datetime.now(UTC) + timedelta(hours=1)).replace(second=0, microsecond=0)
        cron_expression = f"{scheduled_for.minute} {scheduled_for.hour} * * *"
        task_resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "実行付きタスク",
                "cron_expression": cron_expression,
                "timezone": "UTC",
                "estimated_minutes": 45,
            },
        )
        task_id = task_resp.json()["id"]

        execution_resp = client.post(
            "/api/v1/executions",
            json={
                "task_id": task_id,
                "scheduled_for": scheduled_for.isoformat(),
            },
        )
        execution_id = execution_resp.json()["id"]

        resp = client.get("/api/v1/dashboard")

        assert resp.status_code == 200

        data = resp.json()
        all_items = data["today"] + data["overdue"] + data["upcoming"]
        matched_item = next(
            item
            for item in all_items
            if item["task_id"] == task_id
            and datetime.fromisoformat(item["scheduled_for"]).replace(tzinfo=UTC) == scheduled_for
        )
        assert_dashboard_item_contract(matched_item)
        assert matched_item["estimated_minutes"] == 45
        assert matched_item["execution_id"] == execution_id
        assert matched_item["status"] == "in_progress"

    def test_dashboard_is_tenant_isolated(self, tenant_client_factory) -> None:
        with tenant_client_factory() as owner_client:
            owner_client.post(
                "/api/v1/tasks",
                json={"title": "owner-only dashboard task", "cron_expression": "0 10 * * *"},
            )

        with tenant_client_factory(ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB) as other_client:
            resp = other_client.get("/api/v1/dashboard")

        assert resp.status_code == 200
        assert resp.json() == {"today": [], "overdue": [], "upcoming": []}
