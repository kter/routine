export interface DashboardTaskDto {
  taskId: string;
  title: string;
  scheduledFor: string;
  estimatedMinutes: number;
  executionId?: string;
  status?: "in_progress" | "completed";
}

export interface DashboardDataDto {
  today: DashboardTaskDto[];
  overdue: DashboardTaskDto[];
  upcoming: DashboardTaskDto[];
}
