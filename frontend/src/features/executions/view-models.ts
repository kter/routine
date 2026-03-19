import { formatDate } from "@/lib/utils";
import type { Execution, ExecutionStatus } from "./types";

export interface ExecutionLogStepViewModel {
  id: string;
  title: string;
  status: "completed" | "skipped" | "pending";
  evidenceText?: string;
  skippedLabel?: string;
  completedLabel?: string;
}

export interface ExecutionLogViewModel {
  title: string;
  status: ExecutionStatus;
  startedLabel: string;
  completedLabel?: string;
  durationLabel?: string;
  notes?: string;
  stepHeading: string;
  statusBorderColor: string;
  steps: ExecutionLogStepViewModel[];
}

export function getExecutionScreenTitle(execution: Execution): string {
  return execution.taskTitle ?? "タスク実行";
}

export function toExecutionLogViewModel(
  execution: Execution,
): ExecutionLogViewModel {
  return {
    title: execution.taskTitle ?? "実行ログ",
    status: execution.status,
    startedLabel: `開始: ${formatDate(execution.startedAt)}`,
    completedLabel: execution.completedAt
      ? `完了: ${formatDate(execution.completedAt)}`
      : undefined,
    durationLabel:
      execution.durationSeconds != null
        ? `${Math.ceil(execution.durationSeconds / 60)}分`
        : undefined,
    notes: execution.notes || undefined,
    stepHeading: `Step Log — ${execution.steps.length} steps`,
    statusBorderColor:
      execution.status === "completed"
        ? "3px solid hsl(160 60% 45%)"
        : execution.status === "abandoned"
          ? "3px solid hsl(0 72% 54%)"
          : "3px solid hsl(43 96% 56%)",
    steps: execution.steps.map((step) => ({
      id: step.id,
      title: step.stepSnapshot.title,
      status: step.status,
      evidenceText: step.evidenceText || undefined,
      skippedLabel: step.status === "skipped" ? "Skip" : undefined,
      completedLabel: step.completedAt
        ? `${formatDate(step.completedAt)} · ${step.completedBy}`
        : undefined,
    })),
  };
}
