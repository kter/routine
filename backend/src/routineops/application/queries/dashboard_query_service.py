"""Compatibility facade for the dashboard query service.

Canonical imports live under ``routineops.application.dashboard``.
This module remains temporarily to avoid breaking older imports during the
architecture transition.
"""

from routineops.application.dashboard.query_service import (
    DashboardData,
    DashboardItem,
    DashboardQueryService,
)

__all__ = ["DashboardData", "DashboardItem", "DashboardQueryService"]
