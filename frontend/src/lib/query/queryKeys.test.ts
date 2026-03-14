import { describe, expect, it } from "vitest";
import { queryKeys } from "./queryKeys";

describe("queryKeys", () => {
  it("builds stable task detail keys", () => {
    expect(queryKeys.tasks.detail("task-123")).toEqual(["tasks", "task-123"]);
  });

  it("builds stable execution detail keys", () => {
    expect(queryKeys.executions.detail("exec-123")).toEqual([
      "executions",
      "exec-123",
    ]);
  });
});
