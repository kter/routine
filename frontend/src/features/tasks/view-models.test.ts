import { describe, expect, it } from "vitest";
import { toTaskDetailViewModel, toTaskFormViewModel } from "./view-models";

describe("toTaskFormViewModel", () => {
  it("builds task form defaults from a task domain model", () => {
    const viewModel = toTaskFormViewModel({
      id: "task-1",
      tenantId: "tenant-1",
      title: "Daily check",
      description: "Check the dashboard",
      cronExpression: "0 10 * * *",
      timezone: "Asia/Tokyo",
      estimatedMinutes: 15,
      isActive: true,
      tags: ["daily", "ops"],
      createdBy: "user-1",
      createdAt: "2026-03-14T00:00:00Z",
      updatedAt: "2026-03-14T00:00:00Z",
      steps: [
        {
          id: "step-1",
          taskId: "task-1",
          position: 1,
          title: "Open dashboard",
          instruction: "Confirm overnight jobs",
          evidenceType: "text",
          isRequired: true,
          createdAt: "2026-03-14T00:00:00Z",
          updatedAt: "2026-03-14T00:00:00Z",
        },
      ],
    });

    expect(viewModel.defaultValues.tags).toBe("daily, ops");
    expect(viewModel.defaultValues.estimatedMinutes).toBe(15);
    expect(viewModel.defaultSteps).toEqual([
      {
        position: 1,
        title: "Open dashboard",
        instruction: "Confirm overnight jobs",
        evidenceType: "text",
        isRequired: true,
      },
    ]);
  });
});

describe("toTaskDetailViewModel", () => {
  it("derives task detail labels and step badges", () => {
    const viewModel = toTaskDetailViewModel({
      id: "task-1",
      tenantId: "tenant-1",
      title: "Daily check",
      description: "Check the dashboard",
      cronExpression: "0 10 * * *",
      timezone: "Asia/Tokyo",
      estimatedMinutes: 15,
      isActive: false,
      tags: ["daily", "ops"],
      createdBy: "user-1",
      createdAt: "2026-03-14T00:00:00Z",
      updatedAt: "2026-03-14T00:00:00Z",
      steps: [
        {
          id: "step-1",
          taskId: "task-1",
          position: 1,
          title: "Open dashboard",
          instruction: "Confirm overnight jobs",
          evidenceType: "text",
          isRequired: true,
          createdAt: "2026-03-14T00:00:00Z",
          updatedAt: "2026-03-14T00:00:00Z",
        },
      ],
    });

    expect(viewModel.status).toBe("abandoned");
    expect(viewModel.editHref).toBe("/tasks/task-1/edit");
    expect(viewModel.estimatedMinutesLabel).toBe("15分");
    expect(viewModel.tagsLabel).toBe("daily, ops");
    expect(viewModel.steps[0]?.evidenceLabel).toBe("[text]");
    expect(viewModel.deleteDescription).toContain("Daily check");
  });
});
