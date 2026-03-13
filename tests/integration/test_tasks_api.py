"""Integration tests for Tasks API - CRUD E2E."""

from uuid import UUID

from fastapi.testclient import TestClient

from tests.integration.conftest import ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB, TEST_USER_SUB


def assert_task_response_contract(task: dict, *, expected_step_count: int) -> None:
    assert set(task) == {
        "id",
        "tenant_id",
        "title",
        "description",
        "cron_expression",
        "timezone",
        "estimated_minutes",
        "is_active",
        "tags",
        "created_by",
        "created_at",
        "updated_at",
        "steps",
    }
    UUID(task["id"])
    UUID(task["tenant_id"])
    assert isinstance(task["title"], str)
    assert isinstance(task["description"], str)
    assert isinstance(task["cron_expression"], str)
    assert isinstance(task["timezone"], str)
    assert isinstance(task["estimated_minutes"], int)
    assert isinstance(task["is_active"], bool)
    assert isinstance(task["tags"], list)
    assert task["created_by"] == TEST_USER_SUB
    assert isinstance(task["created_at"], str)
    assert isinstance(task["updated_at"], str)
    assert isinstance(task["steps"], list)
    assert len(task["steps"]) == expected_step_count


def assert_step_response_contract(step: dict, *, task_id: str) -> None:
    assert set(step) == {
        "id",
        "task_id",
        "position",
        "title",
        "instruction",
        "evidence_type",
        "is_required",
        "created_at",
        "updated_at",
    }
    UUID(step["id"])
    assert step["task_id"] == task_id
    assert isinstance(step["position"], int)
    assert isinstance(step["title"], str)
    assert isinstance(step["instruction"], str)
    assert isinstance(step["evidence_type"], str)
    assert isinstance(step["is_required"], bool)
    assert isinstance(step["created_at"], str)
    assert isinstance(step["updated_at"], str)


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
        assert_task_response_contract(data, expected_step_count=0)
        assert data["title"] == "テストタスク"
        assert data["cron_expression"] == "0 10 * * *"

    def test_returns_full_contract_with_defaults(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "既定値タスク",
                "cron_expression": "5 11 * * 1-5",
            },
        )

        assert resp.status_code == 201

        data = resp.json()
        assert_task_response_contract(data, expected_step_count=0)
        assert data["description"] == ""
        assert data["timezone"] == "Asia/Tokyo"
        assert data["estimated_minutes"] == 30
        assert data["is_active"] is True
        assert data["tags"] == []

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
        assert_task_response_contract(data, expected_step_count=1)
        assert len(data["steps"]) == 1
        assert data["steps"][0]["title"] == "ステップ1"
        assert_step_response_contract(data["steps"][0], task_id=data["id"])

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
        data = resp.json()
        assert len(data) == 2
        assert [task["title"] for task in data] == ["T2", "T1"]
        for task in data:
            assert_task_response_contract(task, expected_step_count=0)


class TestGetTask:
    def test_gets_existing_task(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "詳細タスク", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert_task_response_contract(data, expected_step_count=0)
        assert data["id"] == task_id

    def test_returns_404_for_missing_task(self, client: TestClient) -> None:
        resp = client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000999")
        assert resp.status_code == 404
        assert resp.json() == {
            "detail": "Task with id '00000000-0000-0000-0000-000000000999' not found"
        }


class TestUpdateTask:
    def test_updates_task_title(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "旧タイトル", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"title": "新タイトル"})
        assert resp.status_code == 200
        data = resp.json()
        assert_task_response_contract(data, expected_step_count=0)
        assert data["title"] == "新タイトル"

    def test_updates_active_status(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "Active Task", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"is_active": False})
        assert resp.status_code == 200
        data = resp.json()
        assert_task_response_contract(data, expected_step_count=0)
        assert data["is_active"] is False

    def test_updates_metadata_fields_and_preserves_unrelated_fields(
        self,
        client: TestClient,
    ) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "Metadata Task",
                "description": "before",
                "cron_expression": "0 10 * * *",
                "estimated_minutes": 25,
                "tags": ["ops"],
            },
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "description": "after",
                "timezone": "UTC",
                "tags": ["ops", "nightly"],
            },
        )

        assert resp.status_code == 200

        data = resp.json()
        assert_task_response_contract(data, expected_step_count=0)
        assert data["description"] == "after"
        assert data["timezone"] == "UTC"
        assert data["tags"] == ["ops", "nightly"]
        assert data["title"] == "Metadata Task"
        assert data["estimated_minutes"] == 25

    def test_returns_422_for_invalid_estimated_minutes_on_update(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={"title": "Bad estimate", "cron_expression": "0 10 * * *"},
        )

        resp = client.patch(
            f"/api/v1/tasks/{create_resp.json()['id']}",
            json={"estimated_minutes": 0},
        )

        assert resp.status_code == 422

    def test_keeps_existing_steps_when_steps_are_not_sent(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "手順保持タスク",
                "cron_expression": "0 10 * * *",
                "steps": [
                    {
                        "position": 1,
                        "title": "既存手順",
                        "instruction": "保持される説明",
                        "evidence_type": "text",
                        "is_required": True,
                    }
                ],
            },
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"title": "更新後タイトル"})

        assert resp.status_code == 200

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        data = get_resp.json()
        assert get_resp.status_code == 200
        assert data["title"] == "更新後タイトル"
        assert len(data["steps"]) == 1
        assert data["steps"][0]["title"] == "既存手順"
        assert data["steps"][0]["instruction"] == "保持される説明"

    def test_updates_steps_and_persists_them(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "手順更新タスク",
                "cron_expression": "0 10 * * *",
                "steps": [
                    {
                        "position": 1,
                        "title": "旧手順",
                        "instruction": "更新前の説明",
                        "evidence_type": "text",
                        "is_required": True,
                    }
                ],
            },
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "steps": [
                    {
                        "position": 1,
                        "title": "新手順",
                        "instruction": "更新後の説明",
                        "evidence_type": "image",
                        "is_required": False,
                    },
                    {
                        "position": 2,
                        "title": "承認依頼",
                        "instruction": "Slack に共有する",
                        "evidence_type": "text",
                        "is_required": True,
                    },
                ]
            },
        )

        assert resp.status_code == 200

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        data = get_resp.json()
        assert get_resp.status_code == 200
        assert data["steps"] == [
            {
                "id": data["steps"][0]["id"],
                "task_id": task_id,
                "position": 1,
                "title": "新手順",
                "instruction": "更新後の説明",
                "evidence_type": "image",
                "is_required": False,
                "created_at": data["steps"][0]["created_at"],
                "updated_at": data["steps"][0]["updated_at"],
            },
            {
                "id": data["steps"][1]["id"],
                "task_id": task_id,
                "position": 2,
                "title": "承認依頼",
                "instruction": "Slack に共有する",
                "evidence_type": "text",
                "is_required": True,
                "created_at": data["steps"][1]["created_at"],
                "updated_at": data["steps"][1]["updated_at"],
            },
        ]

    def test_clears_steps_when_empty_list_is_sent(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={
                "title": "手順削除タスク",
                "cron_expression": "0 10 * * *",
                "steps": [
                    {
                        "position": 1,
                        "title": "削除対象手順",
                        "instruction": "削除前の説明",
                        "evidence_type": "none",
                        "is_required": True,
                    }
                ],
            },
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"steps": []})

        assert resp.status_code == 200

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["steps"] == []

    def test_applies_step_defaults_when_updating_steps(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks",
            json={"title": "手順既定値タスク", "cron_expression": "0 10 * * *"},
        )
        task_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"steps": [{"position": 1, "title": "既定値ステップ"}]},
        )

        assert resp.status_code == 200

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        data = get_resp.json()
        assert get_resp.status_code == 200
        assert data["steps"] == [
            {
                "id": data["steps"][0]["id"],
                "task_id": task_id,
                "position": 1,
                "title": "既定値ステップ",
                "instruction": "",
                "evidence_type": "none",
                "is_required": True,
                "created_at": data["steps"][0]["created_at"],
                "updated_at": data["steps"][0]["updated_at"],
            }
        ]


class TestDeleteTask:
    def test_deletes_existing_task(self, client: TestClient) -> None:
        create_resp = client.post(
            "/api/v1/tasks", json={"title": "削除タスク", "cron_expression": "0 10 * * *"}
        )
        task_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 204
        assert resp.content == b""

        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_returns_404_for_missing_task(self, client: TestClient) -> None:
        resp = client.delete("/api/v1/tasks/00000000-0000-0000-0000-000000000999")
        assert resp.status_code == 404
        assert resp.json() == {
            "detail": "Task with id '00000000-0000-0000-0000-000000000999' not found"
        }


class TestTaskTenantIsolation:
    def test_other_tenant_cannot_get_update_or_delete_task(self, tenant_client_factory) -> None:
        with tenant_client_factory() as owner_client:
            create_resp = owner_client.post(
                "/api/v1/tasks",
                json={"title": "Tenant private task", "cron_expression": "0 10 * * *"},
            )
            task_id = create_resp.json()["id"]

        with tenant_client_factory(ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB) as other_client:
            get_resp = other_client.get(f"/api/v1/tasks/{task_id}")
            patch_resp = other_client.patch(f"/api/v1/tasks/{task_id}", json={"title": "tampered"})
            delete_resp = other_client.delete(f"/api/v1/tasks/{task_id}")

        expected = {"detail": f"Task with id '{task_id}' not found"}
        assert get_resp.status_code == 404
        assert get_resp.json() == expected
        assert patch_resp.status_code == 404
        assert patch_resp.json() == expected
        assert delete_resp.status_code == 404
        assert delete_resp.json() == expected

    def test_other_tenant_does_not_see_task_in_list(self, tenant_client_factory) -> None:
        with tenant_client_factory() as owner_client:
            owner_client.post(
                "/api/v1/tasks",
                json={"title": "Visible only to owner", "cron_expression": "0 10 * * *"},
            )

        with tenant_client_factory(ALT_TEST_TENANT_ID, ALT_TEST_USER_SUB) as other_client:
            resp = other_client.get("/api/v1/tasks")

        assert resp.status_code == 200
        assert resp.json() == []
