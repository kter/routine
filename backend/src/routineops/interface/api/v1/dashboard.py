from typing import Annotated

from fastapi import APIRouter, Depends

from routineops.interface.api.deps import RequestContextDep, get_dashboard_usecases
from routineops.interface.schemas.dashboard import DashboardResponse, DashboardTaskItem
from routineops.usecases.dashboard_usecases import DashboardUsecases

router = APIRouter()
DashboardUsecasesDep = Annotated[DashboardUsecases, Depends(get_dashboard_usecases)]


@router.get("", response_model=DashboardResponse)
def get_dashboard(context: RequestContextDep, usecases: DashboardUsecasesDep) -> DashboardResponse:
    _ = context
    data = usecases.get_dashboard()
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
