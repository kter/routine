export interface Step {
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
  steps?: Step[];
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  cronExpression: string;
  timezone?: string;
  estimatedMinutes?: number;
  tags?: string[];
  steps?: CreateStepRequest[];
}

export interface CreateStepRequest {
  position: number;
  title: string;
  instruction?: string;
  evidenceType?: "none" | "text" | "image";
  isRequired?: boolean;
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {}
