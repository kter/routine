import { formatDate } from "@/lib/utils";
import type { DashboardTask } from "./types";

export interface DashboardTaskViewModel {
  taskId: string;
  title: string;
  taskHref: string;
  scheduledLabel: string;
  estimatedMinutesLabel: string;
  executionId?: string;
  status?: "in_progress" | "completed";
  canStart: boolean;
}

export function toDashboardTaskViewModel(
  task: DashboardTask,
): DashboardTaskViewModel {
  return {
    taskId: task.taskId,
    title: task.title,
    taskHref: `/tasks/${task.taskId}`,
    scheduledLabel: formatDate(task.scheduledFor),
    estimatedMinutesLabel: `${task.estimatedMinutes}分`,
    executionId: task.executionId,
    status: task.status,
    canStart: !task.status,
  };
}
