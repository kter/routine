import os
from unittest.mock import patch
from uuid import UUID

from fastapi.security import HTTPAuthorizationCredentials

from routineops.app.request_context import RequestContext
from routineops.config.settings import clear_settings_caches
from routineops.interface.api.deps import (
    get_dashboard_usecases,
    get_execution_usecases,
    get_request_context,
    get_storage,
    get_task_usecases,
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


def test_get_task_usecases_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()

    with patch(
        "routineops.interface.api.deps.build_task_usecases",
        return_value="task-usecases",
    ) as build_task_usecases:
        usecases = get_task_usecases(context, db)

    assert usecases == "task-usecases"
    build_task_usecases.assert_called_once_with(db=db, context=context)


def test_get_execution_usecases_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()
    storage = object()

    with patch(
        "routineops.interface.api.deps.build_execution_usecases",
        return_value="execution-usecases",
    ) as build_execution_usecases:
        usecases = get_execution_usecases(context, db, storage)

    assert usecases == "execution-usecases"
    build_execution_usecases.assert_called_once_with(
        db=db,
        context=context,
        storage=storage,
    )


def test_get_dashboard_usecases_delegates_to_container() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000111"),
        user_sub="user-sub",
    )
    db = object()

    with patch(
        "routineops.interface.api.deps.build_dashboard_usecases",
        return_value="dashboard-usecases",
    ) as build_dashboard_usecases:
        usecases = get_dashboard_usecases(context, db)

    assert usecases == "dashboard-usecases"
    build_dashboard_usecases.assert_called_once_with(db=db, context=context)


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
