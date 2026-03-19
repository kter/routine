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
