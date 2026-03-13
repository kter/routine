"""Integration tests for Executions API - wizard flow E2E."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from tests.integration.conftest import (
    ALT_TEST_TENANT_ID,
    ALT_TEST_USER_SUB,
    TEST_TENANT_ID,
    TEST_USER_SUB,
)


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


def create_task_with_image_step(client: TestClient) -> dict:
    resp = client.post(
        "/api/v1/tasks",
        json={
            "title": "画像証跡タスク",
            "cron_expression": "0 10 * * *",
            "steps": [
                {
                    "position": 1,
                    "title": "画像アップロード",
                    "instruction": "スクリーンショットを提出",
                    "evidence_type": "image",
                    "is_required": True,
                }
            ],
        },
    )
    assert resp.status_code == 201
    return resp.json()


def assert_execution_step_contract(step: dict, *, execution_id: str) -> None:
    assert set(step) == {
        "id",
        "execution_id",
        "step_id",
        "position",
        "step_snapshot",
        "status",
        "evidence_text",
        "evidence_image_key",
        "evidence_image_url",
        "completed_at",
        "completed_by",
        "notes",
    }
    UUID(step["id"])
    UUID(step["step_id"])
    assert step["execution_id"] == execution_id
    assert isinstance(step["position"], int)
    assert isinstance(step["step_snapshot"], dict)
    assert isinstance(step["status"], str)
    assert step["evidence_image_url"] is None
    assert isinstance(step["notes"], str)


def assert_execution_contract(execution: dict, *, expected_step_count: int) -> None:
    assert set(execution) == {
        "id",
        "tenant_id",
        "task_id",
        "task_title",
        "started_by",
        "status",
        "scheduled_for",
        "started_at",
        "completed_at",
        "duration_seconds",
        "notes",
        "steps",
    }
    UUID(execution["id"])
    UUID(execution["tenant_id"])
    UUID(execution["task_id"])
    assert execution["tenant_id"] == str(TEST_TENANT_ID)
    assert execution["task_title"] is None
    assert execution["started_by"] == TEST_USER_SUB
    assert isinstance(execution["status"], str)
    assert isinstance(execution["started_at"], str)
    assert isinstance(execution["notes"], str)
    assert isinstance(execution["steps"], list)
    assert len(execution["steps"]) == expected_step_count
    for step in execution["steps"]:
        assert_execution_step_contract(step, execution_id=execution["id"])


class TestStartExecution:
    def test_starts_execution_successfully(self, client: TestClient) -> None:
        task = create_task_with_steps(client)

        resp = client.post(
            "/api/v1/executions",
            json={"task_id": task["id"]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert_execution_contract(data, expected_step_count=2)
        assert data["task_id"] == task["id"]
        assert data["status"] == "in_progress"
        assert len(data["steps"]) == 2

    def test_round_trips_scheduled_for_and_notes(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        scheduled_for = datetime(2026, 3, 13, 10, 0, tzinfo=UTC)

        resp = client.post(
            "/api/v1/executions",
            json={
                "task_id": task["id"],
                "scheduled_for": scheduled_for.isoformat(),
                "notes": "朝会前に実施",
            },
        )

        assert resp.status_code == 201

        data = resp.json()
        assert_execution_contract(data, expected_step_count=2)
        assert datetime.fromisoformat(data["scheduled_for"]).replace(tzinfo=UTC) == scheduled_for
        assert data["notes"] == "朝会前に実施"

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
        assert resp.json() == {
            "detail": "Task with id '00000000-0000-0000-0000-000000000999' not found"
        }

    def test_returns_422_for_inactive_task(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        deactivate_resp = client.patch(f"/api/v1/tasks/{task['id']}", json={"is_active": False})
        assert deactivate_resp.status_code == 200

        resp = client.post("/api/v1/executions", json={"task_id": task["id"]})

        assert resp.status_code == 422
        assert resp.json() == {"detail": "Task 'ウィザードフローテスト' is not active"}


class TestListAndGetExecutions:
    def test_lists_executions_newest_first_with_full_contract(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        first = client.post("/api/v1/executions", json={"task_id": task["id"], "notes": "first"})
        second = client.post("/api/v1/executions", json={"task_id": task["id"], "notes": "second"})

        assert first.status_code == 201
        assert second.status_code == 201

        resp = client.get("/api/v1/executions")
        assert resp.status_code == 200

        data = resp.json()
        assert len(data) == 2
        assert [execution["notes"] for execution in data] == ["second", "first"]
        for execution in data:
            assert_execution_contract(execution, expected_step_count=0)

    def test_gets_existing_execution_with_full_contract(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        create_resp = client.post("/api/v1/executions", json={"task_id": task["id"]})
        execution_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/executions/{execution_id}")

        assert resp.status_code == 200

        data = resp.json()
        assert_execution_contract(data, expected_step_count=2)
        assert data["id"] == execution_id

    def test_returns_404_for_missing_execution(self, client: TestClient) -> None:
        resp = client.get("/api/v1/executions/00000000-0000-0000-0000-000000000999")

        assert resp.status_code == 404
        assert resp.json() == {
            "detail": "Execution with id '00000000-0000-0000-0000-000000000999' not found"
        }


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
        data = resp.json()
        assert_execution_step_contract(data, execution_id=execution["id"])
        assert data["status"] == "completed"
        assert data["evidence_text"] == "パッチ確認完了。問題なし。"
        assert data["completed_by"] == TEST_USER_SUB

    def test_returns_422_when_text_evidence_missing(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={},
        )
        assert resp.status_code == 422
        assert resp.json() == {"detail": "Evidence text is required for this step"}

    def test_returns_422_when_image_evidence_missing(self, client: TestClient) -> None:
        task = create_task_with_image_step(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={},
        )

        assert resp.status_code == 422
        assert resp.json() == {"detail": "Evidence image is required for this step"}

    def test_returns_422_when_completing_step_twice(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        first_resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={"evidence_text": "done"},
        )
        second_resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/complete",
            json={"evidence_text": "done again"},
        )

        assert first_resp.status_code == 200
        assert second_resp.status_code == 422
        assert second_resp.json() == {"detail": "Step is already 'completed'"}


class TestSkipStep:
    def test_skips_optional_step(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        optional_step_id = execution["steps"][1]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{optional_step_id}/skip",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert_execution_step_contract(data, execution_id=execution["id"])
        assert data["status"] == "skipped"

    def test_cannot_skip_required_step(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        required_step_id = execution["steps"][0]["id"]

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{required_step_id}/skip",
        )
        assert resp.status_code == 422
        assert resp.json() == {"detail": "Cannot skip a required step"}


class TestCompleteExecution:
    def _complete_all_required_steps(self, client: TestClient, execution: dict) -> None:
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

    def test_completes_execution_after_all_required_steps(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        self._complete_all_required_steps(client, execution)

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/complete",
            json={"notes": "全ステップ完了"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert_execution_contract(data, expected_step_count=0)
        assert data["status"] == "completed"
        assert data["notes"] == "全ステップ完了"
        assert data["completed_at"] is not None
        assert isinstance(data["duration_seconds"], int)

    def test_cannot_complete_with_pending_required_step(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/complete",
            json={},
        )
        assert resp.status_code == 422
        assert resp.json() == {"detail": "1 required step(s) are not completed"}

    def test_cannot_complete_step_after_execution_completed(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        self._complete_all_required_steps(client, execution)
        complete_resp = client.patch(f"/api/v1/executions/{execution['id']}/complete", json={})
        assert complete_resp.status_code == 200

        step_resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{execution['steps'][1]['id']}/skip"
        )

        assert step_resp.status_code == 422
        assert step_resp.json() == {"detail": "Cannot modify execution in status 'completed'"}


class TestAbandonExecution:
    def test_abandons_in_progress_execution(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/abandon",
            json={"notes": "緊急割り込みのため中断"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert_execution_contract(data, expected_step_count=0)
        assert data["status"] == "abandoned"
        assert data["notes"] == "緊急割り込みのため中断"

    def test_cannot_complete_step_after_execution_abandoned(self, client: TestClient) -> None:
        task = create_task_with_steps(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        abandon_resp = client.patch(f"/api/v1/executions/{execution['id']}/abandon", json={})
        assert abandon_resp.status_code == 200

        resp = client.patch(
            f"/api/v1/executions/{execution['id']}/steps/{execution['steps'][0]['id']}/complete",
            json={"evidence_text": "late write"},
        )

        assert resp.status_code == 422
        assert resp.json() == {"detail": "Cannot modify execution in status 'abandoned'"}


class TestEvidenceUploadUrl:
    def test_returns_upload_url_contract_and_storage_key(
        self,
        client: TestClient,
        mock_storage,
    ) -> None:
        task = create_task_with_image_step(client)
        execution = client.post("/api/v1/executions", json={"task_id": task["id"]}).json()
        step_id = execution["steps"][0]["id"]

        resp = client.post(
            f"/api/v1/executions/{execution['id']}/steps/{step_id}/evidence-url",
            json={"content_type": "image/png"},
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "upload_url": "https://s3.example.com/presigned-url",
            "key": f"evidence/{TEST_TENANT_ID}/{execution['id']}/{step_id}",
        }
        mock_storage.generate_upload_url.assert_called_once_with(
            f"evidence/{TEST_TENANT_ID}/{execution['id']}/{step_id}",
            "image/png",
        )

    def test_returns_404_for_missing_execution(self, client: TestClient) -> None:
        step_id = "00000000-0000-0000-0000-000000000123"

        resp = client.post(
            f"/api/v1/executions/00000000-0000-0000-0000-000000000999/steps/{step_id}/evidence-url",
            json={"content_type": "image/png"},
        )

        assert resp.status_code == 404
        assert resp.json() == {
            "detail": "Execution with id '00000000-0000-0000-0000-000000000999' not found"
        }


class TestExecutionTenantIsolation:
    def test_other_tenant_cannot_get_or_mutate_execution(self, tenant_client_factory) -> None:
        with tenant_client_factory() as owner_client:
            task = create_task_with_steps(owner_client)
            execution = owner_client.post("/api/v1/executions", json={"task_id": task["id"]}).json()

        with tenant_client_factory(ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB) as other_client:
            get_resp = other_client.get(f"/api/v1/executions/{execution['id']}")
            evidence_resp = other_client.post(
                f"/api/v1/executions/{execution['id']}/steps/{execution['steps'][0]['id']}/evidence-url",
                json={"content_type": "image/png"},
            )

        expected = {"detail": f"Execution with id '{execution['id']}' not found"}
        assert get_resp.status_code == 404
        assert get_resp.json() == expected
        assert evidence_resp.status_code == 404
        assert evidence_resp.json() == expected

    def test_other_tenant_does_not_see_execution_in_list(self, tenant_client_factory) -> None:
        with tenant_client_factory() as owner_client:
            task = create_task_with_steps(owner_client)
            owner_client.post("/api/v1/executions", json={"task_id": task["id"]})

        with tenant_client_factory(ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB) as other_client:
            resp = other_client.get("/api/v1/executions")

        assert resp.status_code == 200
        assert resp.json() == []
