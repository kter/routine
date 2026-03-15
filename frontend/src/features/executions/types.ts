export type ExecutionStatus = "in_progress" | "completed" | "abandoned";
export type StepStatus = "pending" | "completed" | "skipped";

export interface ExecutionStep {
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
  status: StepStatus;
  evidenceText?: string;
  evidenceImageKey?: string;
  evidenceImageUrl?: string;
  completedAt?: string;
  completedBy?: string;
  notes: string;
}

export interface Execution {
  id: string;
  tenantId: string;
  taskId: string;
  taskTitle?: string;
  startedBy: string;
  status: ExecutionStatus;
  scheduledFor?: string;
  startedAt: string;
  completedAt?: string;
  durationSeconds?: number;
  notes: string;
  steps: ExecutionStep[];
}

export interface StartExecutionInput {
  taskId: string;
  scheduledFor?: string;
  notes?: string;
}

export interface CompleteStepInput {
  evidenceText?: string;
  evidenceImageKey?: string;
  notes?: string;
}
