from __future__ import annotations

from routineops.app.request_context import RequestContext
from routineops.application.queries.dashboard_query_service import (
    DashboardData,
    DashboardQueryService,
)
from routineops.usecases.interfaces.execution_repository import ExecutionRepositoryPort
from routineops.usecases.interfaces.task_repository import TaskRepositoryPort


class DashboardUsecases:
    def __init__(
        self,
        context: RequestContext,
        task_repo: TaskRepositoryPort | None = None,
        exec_repo: ExecutionRepositoryPort | None = None,
        query_service: DashboardQueryService | None = None,
    ) -> None:
        self._context = context
        if query_service is not None:
            self._query_service = query_service
            return
        if task_repo is None or exec_repo is None:
            raise ValueError(
                "task_repo and exec_repo are required when query_service is not provided"
            )
        self._query_service = DashboardQueryService(task_repo, exec_repo)

    def get_dashboard(self) -> DashboardData:
        return self._query_service.get_dashboard(self._context.tenant_id)
