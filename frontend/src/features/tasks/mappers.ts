import type {
  CreateTaskRequestDto,
  TaskDto,
  TaskStepDto,
  TaskStepInputDto,
  UpdateTaskRequestDto,
} from "@/lib/api/dto/tasks";
import type {
  Task,
  TaskInput,
  TaskStep,
  TaskStepInput,
  TaskUpdateInput,
} from "./types";

function mapTaskStepDto(dto: TaskStepDto): TaskStep {
  return {
    id: dto.id,
    taskId: dto.taskId,
    position: dto.position,
    title: dto.title,
    instruction: dto.instruction,
    evidenceType: dto.evidenceType,
    isRequired: dto.isRequired,
    createdAt: dto.createdAt,
    updatedAt: dto.updatedAt,
  };
}

function toTaskStepInputDto(input: TaskStepInput): TaskStepInputDto {
  return {
    position: input.position,
    title: input.title,
    instruction: input.instruction,
    evidenceType: input.evidenceType,
    isRequired: input.isRequired,
  };
}

export function mapTaskDto(dto: TaskDto): Task {
  return {
    id: dto.id,
    tenantId: dto.tenantId,
    title: dto.title,
    description: dto.description,
    cronExpression: dto.cronExpression,
    timezone: dto.timezone,
    estimatedMinutes: dto.estimatedMinutes,
    isActive: dto.isActive,
    tags: dto.tags,
    createdBy: dto.createdBy,
    createdAt: dto.createdAt,
    updatedAt: dto.updatedAt,
    steps: dto.steps?.map(mapTaskStepDto),
  };
}

export function toCreateTaskRequestDto(input: TaskInput): CreateTaskRequestDto {
  return {
    title: input.title,
    description: input.description,
    cronExpression: input.cronExpression,
    timezone: input.timezone,
    estimatedMinutes: input.estimatedMinutes,
    tags: input.tags,
    steps: input.steps?.map(toTaskStepInputDto),
  };
}

export function toUpdateTaskRequestDto(
  input: TaskUpdateInput,
): UpdateTaskRequestDto {
  return {
    title: input.title,
    description: input.description,
    cronExpression: input.cronExpression,
    timezone: input.timezone,
    estimatedMinutes: input.estimatedMinutes,
    tags: input.tags,
    steps: input.steps?.map(toTaskStepInputDto),
  };
}
