from typing import Annotated

from fastapi import APIRouter, Depends

from routineops.application.dashboard import DashboardService
from routineops.interface.api.deps import RequestContextDep, get_dashboard_service
from routineops.interface.schemas.dashboard import DashboardResponse, DashboardTaskItem

router = APIRouter()
DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]


@router.get("", response_model=DashboardResponse)
def get_dashboard(_context: RequestContextDep, service: DashboardServiceDep) -> DashboardResponse:
    data = service.get_dashboard()
    return DashboardResponse(
        today=[
            DashboardTaskItem(
                task_id=item.task_id,
                title=item.title,
                scheduled_for=item.scheduled_for,
                estimated_minutes=item.estimated_minutes,
                execution_id=item.execution_id,
                status=item.status,
            )
            for item in data.today
        ],
        overdue=[
            DashboardTaskItem(
                task_id=item.task_id,
                title=item.title,
                scheduled_for=item.scheduled_for,
                estimated_minutes=item.estimated_minutes,
                execution_id=item.execution_id,
                status=item.status,
            )
            for item in data.overdue
        ],
        upcoming=[
            DashboardTaskItem(
                task_id=item.task_id,
                title=item.title,
                scheduled_for=item.scheduled_for,
                estimated_minutes=item.estimated_minutes,
                execution_id=item.execution_id,
                status=item.status,
            )
            for item in data.upcoming
        ],
    )
