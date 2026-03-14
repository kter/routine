import { describe, expect, it } from "vitest";
import { mapTaskDto, toCreateTaskRequestDto } from "./mappers";

describe("task mappers", () => {
  it("maps task dto into a domain task", () => {
    const task = mapTaskDto({
      id: "task-1",
      tenantId: "tenant-1",
      title: "Daily check",
      description: "Check systems",
      cronExpression: "0 10 * * *",
      timezone: "Asia/Tokyo",
      estimatedMinutes: 15,
      isActive: true,
      tags: ["ops"],
      createdBy: "user-1",
      createdAt: "2026-03-14T00:00:00Z",
      updatedAt: "2026-03-14T00:00:00Z",
      steps: [
        {
          id: "step-1",
          taskId: "task-1",
          position: 1,
          title: "Open dashboard",
          instruction: "Open it",
          evidenceType: "none",
          isRequired: true,
          createdAt: "2026-03-14T00:00:00Z",
          updatedAt: "2026-03-14T00:00:00Z",
        },
      ],
    });

    expect(task.steps?.[0]?.title).toBe("Open dashboard");
    expect(task.tags).toEqual(["ops"]);
  });

  it("maps task input into a create dto", () => {
    const dto = toCreateTaskRequestDto({
      title: "Daily check",
      cronExpression: "0 10 * * *",
      tags: ["ops"],
      steps: [
        {
          position: 1,
          title: "Open dashboard",
          evidenceType: "text",
        },
      ],
    });

    expect(dto.title).toBe("Daily check");
    expect(dto.steps?.[0]?.evidenceType).toBe("text");
  });
});
