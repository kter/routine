import { describe, expect, it } from "vitest";
import {
  mapExecutionDto,
  toCompleteStepRequestDto,
  toStartExecutionRequestDto,
} from "./mappers";

describe("execution mappers", () => {
  it("maps execution dto into a domain execution", () => {
    const execution = mapExecutionDto({
      id: "exec-1",
      tenantId: "tenant-1",
      taskId: "task-1",
      taskTitle: "Daily check",
      startedBy: "user-1",
      status: "in_progress",
      scheduledFor: "2026-03-14T10:00:00Z",
      startedAt: "2026-03-14T10:00:00Z",
      completedAt: undefined,
      durationSeconds: undefined,
      notes: "",
      steps: [
        {
          id: "exec-step-1",
          executionId: "exec-1",
          stepId: "step-1",
          position: 1,
          stepSnapshot: {
            title: "Open dashboard",
            instruction: "Open it",
            evidenceType: "none",
            isRequired: true,
          },
          status: "pending",
          notes: "",
        },
      ],
    });

    expect(execution.taskTitle).toBe("Daily check");
    expect(execution.steps[0]?.stepSnapshot.title).toBe("Open dashboard");
  });

  it("maps execution inputs into dto payloads", () => {
    expect(
      toStartExecutionRequestDto({ taskId: "task-1", notes: "start" }),
    ).toEqual({
      taskId: "task-1",
      scheduledFor: undefined,
      notes: "start",
    });
    expect(
      toCompleteStepRequestDto({ evidenceText: "done", notes: "checked" }),
    ).toEqual({
      evidenceText: "done",
      evidenceImageKey: undefined,
      notes: "checked",
    });
  });
});
