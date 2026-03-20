import { describe, expect, it } from "vitest";
import {
  formatDashboardDateLabel,
  toDashboardTaskViewModel,
} from "./view-models";

describe("toDashboardTaskViewModel", () => {
  it("derives task links and startability from domain tasks", () => {
    const idleTask = toDashboardTaskViewModel({
      taskId: "task-1",
      title: "Daily check",
      scheduledFor: "2026-03-14T10:00:00Z",
      estimatedMinutes: 15,
    });
    const runningTask = toDashboardTaskViewModel({
      taskId: "task-2",
      title: "Monthly audit",
      scheduledFor: "2026-03-14T10:00:00Z",
      estimatedMinutes: 45,
      status: "in_progress",
      executionId: "exec-2",
    });

    expect(idleTask.taskHref).toBe("/tasks/task-1");
    expect(idleTask.canStart).toBe(true);
    expect(idleTask.estimatedMinutesLabel).toBe("15分");
    expect(runningTask.canStart).toBe(false);
    expect(runningTask.status).toBe("in_progress");
  });
});

describe("formatDashboardDateLabel", () => {
  it("formats the dashboard heading date in ja-JP", () => {
    expect(formatDashboardDateLabel(new Date("2026-03-19T00:00:00Z"))).toBe(
      "2026年3月19日(木)",
    );
  });
});
