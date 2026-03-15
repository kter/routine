import { describe, expect, it } from "vitest";
import { ApiError } from "@/lib/api/client";
import { getQueryError } from "./queryError";

describe("getQueryError", () => {
  it("returns null when no error is present", () => {
    expect(getQueryError(null, "Failed to fetch tasks")).toBeNull();
  });

  it("normalizes api errors into plain errors", () => {
    const error = getQueryError(
      new ApiError(404, "HTTP 404", { detail: "Task not found" }),
      "Failed to fetch task",
    );

    expect(error).toBeInstanceOf(Error);
    expect(error?.message).toBe("Task not found");
  });
});
