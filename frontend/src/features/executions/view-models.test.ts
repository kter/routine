import { describe, expect, it } from "vitest";
import {
  getExecutionScreenTitle,
  toExecutionListItemViewModel,
  toExecutionLogViewModel,
} from "./view-models";

describe("getExecutionScreenTitle", () => {
  it("falls back when a task title is unavailable", () => {
    expect(
      getExecutionScreenTitle({
        id: "exec-1",
        tenantId: "tenant-1",
        taskId: "task-1",
        startedBy: "user-1",
        status: "in_progress",
        startedAt: "2026-03-19T00:00:00Z",
        notes: "",
        steps: [],
      }),
    ).toBe("タスク実行");
  });
});

describe("toExecutionLogViewModel", () => {
  it("formats execution summary and step log labels", () => {
    const viewModel = toExecutionLogViewModel({
      id: "exec-1",
      tenantId: "tenant-1",
      taskId: "task-1",
      taskTitle: "Daily check",
      startedBy: "user-1",
      status: "completed",
      startedAt: "2026-03-19T00:00:00Z",
      completedAt: "2026-03-19T00:15:00Z",
      durationSeconds: 900,
      notes: "Done",
      steps: [
        {
          id: "step-1",
          executionId: "exec-1",
          stepId: "task-step-1",
          position: 1,
          stepSnapshot: {
            title: "Open dashboard",
            instruction: "Confirm overnight jobs",
            evidenceType: "text",
            isRequired: true,
          },
          status: "completed",
          evidenceText: "All clear",
          completedAt: "2026-03-19T00:05:00Z",
          completedBy: "user-1",
          notes: "",
        },
      ],
    });

    expect(viewModel.title).toBe("Daily check");
    expect(viewModel.durationLabel).toBe("15分");
    expect(viewModel.stepHeading).toBe("Step Log — 1 steps");
    expect(viewModel.statusBorderColor).toContain("160 60% 45%");
    expect(viewModel.steps[0]?.completedLabel).toContain("user-1");
  });
});

describe("toExecutionListItemViewModel", () => {
  it("formats list labels and status appearance", () => {
    const viewModel = toExecutionListItemViewModel({
      id: "exec-1",
      tenantId: "tenant-1",
      taskId: "task-1",
      taskTitle: "Daily check",
      startedBy: "user-1",
      status: "in_progress",
      startedAt: "2026-03-19T00:00:00Z",
      durationSeconds: 75,
      notes: "",
      steps: [
        {
          id: "step-1",
          executionId: "exec-1",
          stepId: "task-step-1",
          position: 1,
          stepSnapshot: {
            title: "Open dashboard",
            instruction: "Confirm overnight jobs",
            evidenceType: "text",
            isRequired: true,
          },
          status: "completed",
          notes: "",
        },
        {
          id: "step-2",
          executionId: "exec-1",
          stepId: "task-step-2",
          position: 2,
          stepSnapshot: {
            title: "Review alerts",
            instruction: "",
            evidenceType: "none",
            isRequired: true,
          },
          status: "pending",
          notes: "",
        },
      ],
    });

    expect(viewModel.href).toBe("/executions/exec-1");
    expect(viewModel.statusLabel).toBe("実行中");
    expect(viewModel.stepsLabel).toBe("1/2 steps");
    expect(viewModel.durationLabel).toBe("1m 15s");
    expect(viewModel.isActive).toBe(true);
  });
});
