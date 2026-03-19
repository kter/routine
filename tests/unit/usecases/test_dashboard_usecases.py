"""Unit tests for DashboardUsecases wiring."""

from unittest.mock import MagicMock

from routineops.application.queries.dashboard_query_service import DashboardData
from routineops.usecases.dashboard_usecases import DashboardUsecases


def test_get_dashboard_delegates_to_query_service() -> None:
    query_service = MagicMock()
    expected = DashboardData(today=[], overdue=[], upcoming=[])
    query_service.get_dashboard.return_value = expected
    usecases = DashboardUsecases(query_service=query_service)

    result = usecases.get_dashboard()

    assert result is expected
    query_service.get_dashboard.assert_called_once_with()
