export type ExecutionStatusDto = "in_progress" | "completed" | "abandoned";
export type StepStatusDto = "pending" | "completed" | "skipped";

export interface ExecutionStepDto {
  id: string;
  executionId: string;
  stepId: string;
  position: number;
  stepSnapshot: {
    title: string;
    instruction: string;
    evidenceType: "none" | "text" | "image";
    isRequired: boolean;
  };
  status: StepStatusDto;
  evidenceText?: string;
  evidenceImageKey?: string;
  evidenceImageUrl?: string;
  completedAt?: string;
  completedBy?: string;
  notes: string;
}

export interface ExecutionDto {
  id: string;
  tenantId: string;
  taskId: string;
  taskTitle?: string;
  startedBy: string;
  status: ExecutionStatusDto;
  scheduledFor?: string;
  startedAt: string;
  completedAt?: string;
  durationSeconds?: number;
  notes: string;
  steps: ExecutionStepDto[];
}

export interface StartExecutionRequestDto {
  taskId: string;
  scheduledFor?: string;
  notes?: string;
}

export interface CompleteStepRequestDto {
  evidenceText?: string;
  evidenceImageKey?: string;
  notes?: string;
}
