import type { CSSProperties } from "react";
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

export interface ExecutionListItemViewModel {
  href: string;
  title: string;
  statusLabel: string;
  statusLabelStyle: CSSProperties;
  dotColor: string;
  stripColor: string;
  isActive: boolean;
  startedLabel: string;
  stepsLabel?: string;
  durationLabel?: string;
}

const EXECUTION_LIST_STATUS_CONFIG: Record<
  Execution["status"],
  {
    label: string;
    dotColor: string;
    stripColor: string;
    labelStyle: CSSProperties;
  }
> = {
  in_progress: {
    label: "実行中",
    dotColor: "hsl(43 96% 56%)",
    stripColor: "hsl(43 96% 56%)",
    labelStyle: {
      color: "hsl(43 96% 65%)",
      background: "hsl(43 60% 10%)",
      border: "1px solid hsl(43 60% 18%)",
    },
  },
  completed: {
    label: "完了",
    dotColor: "hsl(160 60% 45%)",
    stripColor: "hsl(160 60% 45%)",
    labelStyle: {
      color: "hsl(160 60% 55%)",
      background: "hsl(160 40% 8%)",
      border: "1px solid hsl(160 40% 15%)",
    },
  },
  abandoned: {
    label: "中断",
    dotColor: "hsl(215 16% 36%)",
    stripColor: "hsl(218 28% 24%)",
    labelStyle: {
      color: "hsl(215 16% 50%)",
      background: "hsl(218 28% 12%)",
      border: "1px solid hsl(218 28% 18%)",
    },
  },
};

export function getExecutionScreenTitle(execution: Execution): string {
  return execution.taskTitle ?? "タスク実行";
}

export function toExecutionListItemViewModel(
  execution: Execution,
): ExecutionListItemViewModel {
  const config = EXECUTION_LIST_STATUS_CONFIG[execution.status];
  const startedAt = new Date(execution.startedAt);
  const completedSteps = execution.steps.filter(
    (step) => step.status === "completed",
  ).length;
  const totalSteps = execution.steps.length;

  return {
    href: `/executions/${execution.id}`,
    title: execution.taskTitle ?? execution.taskId,
    statusLabel: config.label,
    statusLabelStyle: config.labelStyle,
    dotColor: config.dotColor,
    stripColor: config.stripColor,
    isActive: execution.status === "in_progress",
    startedLabel: `${startedAt.toLocaleDateString("ja-JP", {
      month: "numeric",
      day: "numeric",
    })} · ${startedAt.toLocaleTimeString("ja-JP", {
      hour: "2-digit",
      minute: "2-digit",
    })}`,
    stepsLabel:
      totalSteps > 0 ? `${completedSteps}/${totalSteps} steps` : undefined,
    durationLabel:
      execution.durationSeconds != null
        ? formatExecutionDuration(execution.durationSeconds)
        : undefined,
  };
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

function formatExecutionDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return remainingSeconds > 0
    ? `${minutes}m ${remainingSeconds}s`
    : `${minutes}m`;
}
