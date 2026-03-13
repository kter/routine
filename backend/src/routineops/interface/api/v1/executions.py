from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from routineops.domain.entities.execution import Execution
from routineops.interface.api.deps import RequestContextDep, get_execution_usecases
from routineops.interface.schemas.execution import (
    AbandonExecutionRequest,
    CompleteExecutionRequest,
    CompleteStepRequest,
    EvidenceUploadUrlRequest,
    EvidenceUploadUrlResponse,
    ExecutionResponse,
    ExecutionStepResponse,
    StartExecutionRequest,
)
from routineops.usecases.execution_usecases import ExecutionUsecases

router = APIRouter()
ExecUsecasesDep = Annotated[ExecutionUsecases, Depends(get_execution_usecases)]


def _map_execution(execution: Execution, task_title: str | None = None) -> ExecutionResponse:
    return ExecutionResponse(
        id=execution.id,
        tenant_id=execution.tenant_id,
        task_id=execution.task_id,
        task_title=task_title,
        started_by=execution.started_by,
        status=execution.status.value,
        scheduled_for=execution.scheduled_for,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        duration_seconds=execution.duration_seconds,
        notes=execution.notes,
        steps=[
            ExecutionStepResponse(
                id=s.id,
                execution_id=s.execution_id,
                step_id=s.step_id,
                position=s.position,
                step_snapshot=s.step_snapshot,
                status=s.status.value,
                evidence_text=s.evidence_text,
                evidence_image_key=s.evidence_image_key,
                completed_at=s.completed_at,
                completed_by=s.completed_by,
                notes=s.notes,
            )
            for s in execution.steps
        ],
    )


@router.get("", response_model=list[ExecutionResponse])
def list_executions(
    _context: RequestContextDep, usecases: ExecUsecasesDep
) -> list[ExecutionResponse]:
    return [_map_execution(e) for e in usecases.list_executions()]


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(
    execution_id: UUID,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionResponse:
    return _map_execution(usecases.get_execution(execution_id))


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def start_execution(
    body: StartExecutionRequest,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionResponse:
    execution = usecases.start_execution(
        task_id=body.task_id,
        scheduled_for=body.scheduled_for,
        notes=body.notes,
    )
    return _map_execution(execution)


@router.patch("/{execution_id}/steps/{step_id}/complete", response_model=ExecutionStepResponse)
def complete_step(
    execution_id: UUID,
    step_id: UUID,
    body: CompleteStepRequest,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionStepResponse:
    step = usecases.complete_step(
        execution_id=execution_id,
        step_id=step_id,
        evidence_text=body.evidence_text,
        evidence_image_key=body.evidence_image_key,
        notes=body.notes,
    )
    return ExecutionStepResponse(
        id=step.id,
        execution_id=step.execution_id,
        step_id=step.step_id,
        position=step.position,
        step_snapshot=step.step_snapshot,
        status=step.status.value,
        evidence_text=step.evidence_text,
        evidence_image_key=step.evidence_image_key,
        completed_at=step.completed_at,
        completed_by=step.completed_by,
        notes=step.notes,
    )


@router.patch("/{execution_id}/steps/{step_id}/skip", response_model=ExecutionStepResponse)
def skip_step(
    execution_id: UUID,
    step_id: UUID,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionStepResponse:
    step = usecases.skip_step(execution_id, step_id)
    return ExecutionStepResponse(
        id=step.id,
        execution_id=step.execution_id,
        step_id=step.step_id,
        position=step.position,
        step_snapshot=step.step_snapshot,
        status=step.status.value,
        evidence_text=step.evidence_text,
        evidence_image_key=step.evidence_image_key,
        completed_at=step.completed_at,
        completed_by=step.completed_by,
        notes=step.notes,
    )


@router.patch("/{execution_id}/complete", response_model=ExecutionResponse)
def complete_execution(
    execution_id: UUID,
    body: CompleteExecutionRequest,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionResponse:
    return _map_execution(usecases.complete_execution(execution_id, notes=body.notes))


@router.patch("/{execution_id}/abandon", response_model=ExecutionResponse)
def abandon_execution(
    execution_id: UUID,
    body: AbandonExecutionRequest,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> ExecutionResponse:
    return _map_execution(usecases.abandon_execution(execution_id, notes=body.notes))


@router.post(
    "/{execution_id}/steps/{step_id}/evidence-url",
    response_model=EvidenceUploadUrlResponse,
)
def get_evidence_upload_url(
    execution_id: UUID,
    step_id: UUID,
    body: EvidenceUploadUrlRequest,
    _context: RequestContextDep,
    usecases: ExecUsecasesDep,
) -> EvidenceUploadUrlResponse:
    upload_url, key = usecases.get_evidence_upload_url(execution_id, step_id, body.content_type)
    return EvidenceUploadUrlResponse(upload_url=upload_url, key=key)
