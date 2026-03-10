"""Integration tests for Executions API - wizard flow E2E."""
from fastapi.testclient import TestClient


def create_task_with_steps(client: TestClient) -> dict:
    resp = client.post(
        "/api/v1/tasks",
        json={
            "title": "ウィザードフローテスト",
            "cron_expression": "0 10 * * *",
            "steps": [
                {
                    "position": 1,
                    "title": "必須ステップ",
                    "instruction": "確認してください",
                    "evidence_type": "text",
                    "is_required": True,
                },
                {
                    "position": 2,
                    "title": "任意ステップ",
                    "instruction": "スクリーンショット",
                    "evidence_type": "none",
                    "is_required": False,
                },
            ],
        },
    )
    assert resp.status_code == 201
    return resp.json()


class TestStartExecution:
    def test_starts_execution_successfully(self, client: TestClient) -> None:
        task = create_task_with_steps(client)

        resp = client.post(
            "/api/v1/executions",
            json={"task_id": task["id"]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["task_id"] == task["id"]
        assert data["status"] == "in_progress"
        assert len(data["steps"]) == 2

    def test_snapshots_steps_at_start(self, client: TestClient) -> None:
        task = create_task_with_steps(client)

        resp = client.post("/api/v1/executions", json={"task_id": task["id"]})
        execution = resp.json()

        assert execution["steps"][0]["step_snapshot"]["title"] == "必須ステップ"
        assert execution["steps"][0]["status"] == "pending"

    def test_snapshots_updated_steps_after_task_edit(self, client: TestClient) -> None:
        task = create_task_with_steps(client)

        update_resp = client.patch(
            f"/api/v1/tasks/{task['id']}",
            json={
                "steps": [
                    {
                        "position": 1,
                        "title": "更新後ステップ",
                        "instruction": "更新後の手順",
                        "evidence_type": "image",
                        "is_required": False,
                    }
                ]
            },
        )
        assert update_resp.status_code == 200

        resp = client.post("/api/v1/executions", json={"task_id": task["id"]})
        execution = resp.json()

        assert resp.status_code == 201
        assert len(execution["steps"]) == 1
        assert execution["steps"][0]["step_snapshot"] == {
            "title": "更新後ステップ",
            "instruction": "更新後の手順",
            "evidence_type": "image",
            "is_required": False,
        }

    def test_returns_404_for_missing_task(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/executions",
            json={"task_id": "00000000-0000-0000-0000-000000000999"},
        )
        assert resp.status_code == 404


class TestCompleteStep:
    def test_completes_step_with_evidence_text(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={"evidence_text": "パッチ確認完了。問題なし。"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        assert resp.json()["evidence_text"] == "パッチ確認完了。問題なし。"

    def test_returns_422_when_text_evidence_missing(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={},
        )
        assert resp.status_code == 422


class TestSkipStep:
    def test_skips_optional_step(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        optional_step_id = execution["steps"][1]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{optional_step_id}/skip",
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "skipped"

    def test_cannot_skip_required_step(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        required_step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{required_step_id}/skip",
        )
        assert resp.status_code == 422


class TestCompleteExecution:
    def _complete_all_required_steps(
        self, client: TestClient, execution: dict
    ) -> None:
        for step in execution["steps"]:
            if step["step_snapshot"].get("is_required"):
                evidence_type = step["step_snapshot"].get("evidence_type", "none")
                body = {}
                if evidence_type == "text":
                    body = {"evidence_text": "完了"}
                client.patch(
                    f"/api/v1/executions/{execution['id']}/steps/{step['id']}/complete",
                    json=body,
                )

    def test_completes_execution_after_all_required_steps(
        self, client: TestClient
    ) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        self._complete_all_required_steps(client, execution)

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/complete",
            json={"notes": "全ステップ完了"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_cannot_complete_with_pending_required_step(
        self, client: TestClient
    ) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/complete",
            json={},
        )
        assert resp.status_code == 422


class TestAbandonExecution:
    def test_abandons_in_progress_execution(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/abandon",
            json={"notes": "緊急割り込みのため中断"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "abandoned"
