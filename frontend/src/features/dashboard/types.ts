export interface DashboardTask {
  taskId: string;
  title: string;
  scheduledFor: string;
  estimatedMinutes: number;
  executionId?: string;
  status?: "in_progress" | "completed";
}

export interface DashboardData {
  today: DashboardTask[];
  overdue: DashboardTask[];
  upcoming: DashboardTask[];
}
