"""Integration tests for Dashboard API."""

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from routineops.infrastructure.db.models.task_model import TaskModel


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
        titles = [item["title"] for item in all_items]
        assert "不正timezoneタスク" in titles
