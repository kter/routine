export interface TaskStepDto {
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

export interface TaskDto {
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
  steps?: TaskStepDto[];
}

export interface TaskStepInputDto {
  position: number;
  title: string;
  instruction?: string;
  evidenceType?: "none" | "text" | "image";
  isRequired?: boolean;
}

export interface CreateTaskRequestDto {
  title: string;
  description?: string;
  cronExpression: string;
  timezone?: string;
  estimatedMinutes?: number;
  tags?: string[];
  steps?: TaskStepInputDto[];
}

export type UpdateTaskRequestDto = Partial<CreateTaskRequestDto>;
