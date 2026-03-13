"""Unit tests for DashboardUsecases wiring."""

from unittest.mock import MagicMock
from uuid import UUID

from routineops.application.queries.dashboard_query_service import DashboardData
from routineops.usecases.dashboard_usecases import DashboardUsecases

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def test_get_dashboard_delegates_to_query_service() -> None:
    query_service = MagicMock()
    expected = DashboardData(today=[], overdue=[], upcoming=[])
    query_service.get_dashboard.return_value = expected
    usecases = DashboardUsecases(query_service=query_service)

    result = usecases.get_dashboard(TENANT_ID)

    assert result is expected
    query_service.get_dashboard.assert_called_once_with(TENANT_ID)
