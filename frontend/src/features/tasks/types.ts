export interface TaskStep {
  id: string;
  taskId: string;
  position: number;
  title: string;
  instruction: string;
  evidenceType: "none" | "text" | "image";
  isRequired: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: string;
  tenantId: string;
  title: string;
  description: string;
  cronExpression: string;
  timezone: string;
  estimatedMinutes: number;
  isActive: boolean;
  tags: string[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  steps?: TaskStep[];
}

export interface TaskStepInput {
  position: number;
  title: string;
  instruction?: string;
  evidenceType?: "none" | "text" | "image";
  isRequired?: boolean;
}

export interface TaskInput {
  title: string;
  description?: string;
  cronExpression: string;
  timezone?: string;
  estimatedMinutes?: number;
  tags?: string[];
  steps?: TaskStepInput[];
}

export type TaskUpdateInput = Partial<TaskInput>;
