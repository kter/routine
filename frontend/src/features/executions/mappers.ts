import type {
  CompleteStepRequestDto,
  ExecutionDto,
  ExecutionStepDto,
  StartExecutionRequestDto,
} from "@/lib/api/dto/executions";
import type {
  CompleteStepInput,
  Execution,
  ExecutionStep,
  StartExecutionInput,
} from "./types";

function mapExecutionStepDto(dto: ExecutionStepDto): ExecutionStep {
  return {
    id: dto.id,
    executionId: dto.executionId,
    stepId: dto.stepId,
    position: dto.position,
    stepSnapshot: {
      title: dto.stepSnapshot.title,
      instruction: dto.stepSnapshot.instruction,
      evidenceType: dto.stepSnapshot.evidenceType,
      isRequired: dto.stepSnapshot.isRequired,
    },
    status: dto.status,
    evidenceText: dto.evidenceText,
    evidenceImageKey: dto.evidenceImageKey,
    evidenceImageUrl: dto.evidenceImageUrl,
    completedAt: dto.completedAt,
    completedBy: dto.completedBy,
    notes: dto.notes,
  };
}

export function mapExecutionDto(dto: ExecutionDto): Execution {
  return {
    id: dto.id,
    tenantId: dto.tenantId,
    taskId: dto.taskId,
    taskTitle: dto.taskTitle,
    startedBy: dto.startedBy,
    status: dto.status,
    scheduledFor: dto.scheduledFor,
    startedAt: dto.startedAt,
    completedAt: dto.completedAt,
    durationSeconds: dto.durationSeconds,
    notes: dto.notes,
    steps: dto.steps.map(mapExecutionStepDto),
  };
}

export function toStartExecutionRequestDto(
  input: StartExecutionInput,
): StartExecutionRequestDto {
  return {
    taskId: input.taskId,
    scheduledFor: input.scheduledFor,
    notes: input.notes,
  };
}

export function toCompleteStepRequestDto(
  input: CompleteStepInput,
): CompleteStepRequestDto {
  return {
    evidenceText: input.evidenceText,
    evidenceImageKey: input.evidenceImageKey,
    notes: input.notes,
  };
}
