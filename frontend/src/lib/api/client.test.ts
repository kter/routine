import { describe, expect, it } from "vitest";
import { ApiError, getApiErrorMessage, normalizeApiError } from "./client";

describe("getApiErrorMessage", () => {
  it("prefers detail from an API response body", () => {
    expect(getApiErrorMessage({ detail: "Task not found" }, 404)).toBe(
      "Task not found",
    );
  });

  it("falls back to the HTTP status when the response body has no message", () => {
    expect(getApiErrorMessage({ foo: "bar" }, 422)).toBe("HTTP 422");
  });
});

describe("normalizeApiError", () => {
  it("converts ApiError into a plain Error with the API detail message", () => {
    const error = normalizeApiError(
      new ApiError(422, "HTTP 422", { detail: "Invalid cron expression" }),
      "Failed to fetch task",
    );

    expect(error).toBeInstanceOf(Error);
    expect(error.message).toBe("Invalid cron expression");
  });

  it("uses the fallback message for unknown error values", () => {
    expect(normalizeApiError("boom", "Failed to fetch dashboard").message).toBe(
      "Failed to fetch dashboard",
    );
  });
});
