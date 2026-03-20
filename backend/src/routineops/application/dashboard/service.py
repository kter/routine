from __future__ import annotations

from routineops.application.dashboard.query_service import (
    DashboardData,
    DashboardQueryService,
)
from routineops.application.executions.ports import ExecutionRepositoryPort
from routineops.application.tasks.ports import TaskRepositoryPort


class DashboardService:
    def __init__(
        self,
        task_repo: TaskRepositoryPort | None = None,
        exec_repo: ExecutionRepositoryPort | None = None,
        query_service: DashboardQueryService | None = None,
    ) -> None:
        if query_service is not None:
            self._query_service = query_service
            return
        if task_repo is None or exec_repo is None:
            raise ValueError(
                "task_repo and exec_repo are required when query_service is not provided"
            )
        self._query_service = DashboardQueryService(task_repo, exec_repo)

    def get_dashboard(self) -> DashboardData:
        return self._query_service.get_dashboard()
