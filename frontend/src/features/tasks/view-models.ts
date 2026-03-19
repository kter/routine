import { formatCron } from "@/lib/utils";
import type { Task, TaskStepInput } from "./types";

export interface TaskFormDefaultValues {
  title: string;
  description: string;
  cronExpression: string;
  timezone: string;
  estimatedMinutes: number;
  tags: string;
}

export interface TaskFormViewModel {
  defaultValues: TaskFormDefaultValues;
  defaultSteps: TaskStepInput[];
}

export interface TaskDetailStepViewModel {
  id: string;
  position: number;
  title: string;
  instruction: string;
  evidenceLabel?: string;
}

export interface TaskDetailViewModel {
  title: string;
  status: "completed" | "abandoned";
  scheduleLabel: string;
  timezoneLabel: string;
  estimatedMinutesLabel: string;
  tagsLabel?: string;
  editHref: string;
  deleteDescription: string;
  steps: TaskDetailStepViewModel[];
}

export function toTaskFormViewModel(task: Task): TaskFormViewModel {
  return {
    defaultValues: {
      title: task.title,
      description: task.description,
      cronExpression: task.cronExpression,
      timezone: task.timezone,
      estimatedMinutes: task.estimatedMinutes,
      tags: task.tags.join(", "),
    },
    defaultSteps:
      task.steps?.map((step) => ({
        position: step.position,
        title: step.title,
        instruction: step.instruction,
        evidenceType: step.evidenceType,
        isRequired: step.isRequired,
      })) ?? [],
  };
}

export function toTaskDetailViewModel(task: Task): TaskDetailViewModel {
  return {
    title: task.title,
    status: task.isActive ? "completed" : "abandoned",
    scheduleLabel: formatCron(task.cronExpression),
    timezoneLabel: task.timezone,
    estimatedMinutesLabel: `${task.estimatedMinutes}分`,
    tagsLabel: task.tags.length > 0 ? task.tags.join(", ") : undefined,
    editHref: `/tasks/${task.id}/edit`,
    deleteDescription: `「${task.title}」を削除します。この操作は取り消せません。`,
    steps:
      task.steps?.map((step) => ({
        id: step.id,
        position: step.position,
        title: step.title,
        instruction: step.instruction,
        evidenceLabel:
          step.evidenceType !== "none" ? `[${step.evidenceType}]` : undefined,
      })) ?? [],
  };
}
