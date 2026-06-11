import { describe, expect, it } from "vitest";
import { mapDashboardDataDto } from "./mappers";

describe("dashboard mappers", () => {
  it("maps each dashboard section into domain tasks", () => {
    const data = mapDashboardDataDto({
      today: [
        {
          taskId: "task-1",
          title: "Daily check",
          scheduledFor: "2026-06-11T10:00:00Z",
          estimatedMinutes: 15,
          executionId: "exec-1",
          status: "in_progress",
        },
      ],
      overdue: [
        {
          taskId: "task-2",
          title: "Weekly report",
          scheduledFor: "2026-06-09T10:00:00Z",
          estimatedMinutes: 30,
        },
      ],
      upcoming: [],
    });

    expect(data.today).toHaveLength(1);
    expect(data.today[0]).toEqual({
      taskId: "task-1",
      title: "Daily check",
      scheduledFor: "2026-06-11T10:00:00Z",
      estimatedMinutes: 15,
      executionId: "exec-1",
      status: "in_progress",
    });
    expect(data.overdue[0]?.executionId).toBeUndefined();
    expect(data.overdue[0]?.status).toBeUndefined();
    expect(data.upcoming).toEqual([]);
  });

  it("maps empty dashboard data", () => {
    const data = mapDashboardDataDto({ today: [], overdue: [], upcoming: [] });

    expect(data).toEqual({ today: [], overdue: [], upcoming: [] });
  });
});
