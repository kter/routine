import os
from unittest.mock import patch
from uuid import UUID

from fastapi.security import HTTPAuthorizationCredentials

from routineops.app.request_context import RequestContext
from routineops.config.settings import clear_settings_caches
from routineops.interface.api.deps import (
    get_dashboard_service,
    get_execution_service,
    get_request_context,
    get_storage,
    get_task_service,
)


def test_get_request_context_uses_test_mode_settings() -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="ignored")

    with patch.dict(
        os.environ,
        {
            "TEST_MODE": "true",
            "TEST_TENANT_ID": "00000000-0000-0000-0000-000000000777",
            "TEST_USER_SUB": "deps-user",
        },
        clear=False,
    ):
        clear_settings_caches()
        context = get_request_context(credentials)

    assert str(context.tenant_id) == "00000000-0000-0000-0000-000000000777"
    assert context.user_sub == "deps-user"


def test_get_task_service_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()

    with patch(
        "routineops.interface.api.deps.build_task_service",
        return_value="task-service",
    ) as build_task_service:
        service = get_task_service(context, db)

    assert service == "task-service"
    build_task_service.assert_called_once_with(db=db, context=context)


def test_get_execution_service_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()
    storage = object()

    with patch(
        "routineops.interface.api.deps.build_execution_service",
        return_value="execution-service",
    ) as build_execution_service:
        service = get_execution_service(context, db, storage)

    assert service == "execution-service"
    build_execution_service.assert_called_once_with(
        db=db,
        context=context,
        storage=storage,
    )


def test_get_dashboard_service_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()

    with patch(
        "routineops.interface.api.deps.build_dashboard_service",
        return_value="dashboard-service",
    ) as build_dashboard_service:
        service = get_dashboard_service(context, db)

    assert service == "dashboard-service"
    build_dashboard_service.assert_called_once_with(db=db, context=context)


def test_get_storage_uses_settings_bucket_name() -> None:
    with (
        patch(
            "routineops.interface.api.deps.get_api_settings",
        ) as get_api_settings,
        patch(
            "routineops.interface.api.deps.build_storage",
            return_value="storage",
        ) as build_storage,
    ):
        get_api_settings.return_value.evidence_bucket_name = "bucket-name"
        storage = get_storage()

    assert storage == "storage"
    build_storage.assert_called_once_with(bucket_name="bucket-name")
