"""Unit tests for DashboardService wiring."""

from unittest.mock import MagicMock

from routineops.application.dashboard import DashboardData, DashboardService


def test_get_dashboard_delegates_to_query_service() -> None:
    query_service = MagicMock()
    expected = DashboardData(today=[], overdue=[], upcoming=[])
    query_service.get_dashboard.return_value = expected
    service = DashboardService(query_service=query_service)

    result = service.get_dashboard()

    assert result is expected
    query_service.get_dashboard.assert_called_once_with()
