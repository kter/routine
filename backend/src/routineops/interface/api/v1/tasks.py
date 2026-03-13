from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.interface.api.deps import RequestContextDep, get_task_usecases
from routineops.interface.schemas.task import (
    CreateTaskRequest,
    StepResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from routineops.usecases.task_usecases import TaskUsecases

router = APIRouter()
TaskUsecasesDep = Annotated[TaskUsecases, Depends(get_task_usecases)]


def _map_task(task) -> TaskResponse:  # type: ignore[no-untyped-def]

    return TaskResponse(
        id=task.id,
        tenant_id=task.tenant_id,
        title=task.title,
        description=task.description,
        cron_expression=str(task.cron_expression),
        timezone=task.timezone,
        estimated_minutes=task.estimated_minutes,
        is_active=task.is_active,
        tags=task.tags,
        created_by=task.created_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        steps=[
            StepResponse(
                id=s.id,
                task_id=s.task_id,
                position=s.position,
                title=s.title,
                instruction=s.instruction,
                evidence_type=s.evidence_type.value,
                is_required=s.is_required,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in task.steps
        ],
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(context: RequestContextDep, usecases: TaskUsecasesDep) -> list[TaskResponse]:
    _ = context
    return [_map_task(t) for t in usecases.list_tasks()]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, context: RequestContextDep, usecases: TaskUsecasesDep) -> TaskResponse:
    _ = context
    try:
        return _map_task(usecases.get_task(task_id))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    body: CreateTaskRequest,
    context: RequestContextDep,
    usecases: TaskUsecasesDep,
) -> TaskResponse:
    _ = context
    try:
        task = usecases.create_task(
            title=body.title,
            cron_expression=body.cron_expression,
            description=body.description,
            timezone=body.timezone,
            estimated_minutes=body.estimated_minutes,
            tags=body.tags,
            steps=[s.model_dump() for s in body.steps],
        )
        return _map_task(task)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    body: UpdateTaskRequest,
    context: RequestContextDep,
    usecases: TaskUsecasesDep,
) -> TaskResponse:
    _ = context
    try:
        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        return _map_task(usecases.update_task(task_id, **updates))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, context: RequestContextDep, usecases: TaskUsecasesDep) -> None:
    _ = context
    try:
        usecases.delete_task(task_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
