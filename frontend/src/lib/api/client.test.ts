import { beforeEach, describe, expect, it, vi } from "vitest";

const sentryMocks = vi.hoisted(() => {
  const getIdToken = vi.fn();
  const addBreadcrumb = vi.fn();
  const captureException = vi.fn();
  const setTag = vi.fn();
  const setContext = vi.fn();
  const withScope = vi.fn(
    (
      callback: (scope: {
        setTag: typeof setTag;
        setContext: typeof setContext;
      }) => void,
    ) => {
      callback({
        setTag,
        setContext,
      });
    },
  );

  return {
    addBreadcrumb,
    captureException,
    getIdToken,
    setContext,
    setTag,
    withScope,
  };
});

vi.mock("@/lib/auth/cognito", () => ({
  getIdToken: sentryMocks.getIdToken,
}));

vi.mock("@sentry/react", () => ({
  addBreadcrumb: sentryMocks.addBreadcrumb,
  captureException: sentryMocks.captureException,
  withScope: sentryMocks.withScope,
}));

import {
  ApiError,
  apiClient,
  createRequestId,
  getApiErrorMessage,
  normalizeApiError,
} from "./client";

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

describe("createRequestId", () => {
  it("returns a non-empty identifier", () => {
    expect(createRequestId()).toBeTruthy();
  });
});

describe("apiClient", () => {
  beforeEach(() => {
    sentryMocks.getIdToken.mockReset();
    sentryMocks.addBreadcrumb.mockReset();
    sentryMocks.captureException.mockReset();
    sentryMocks.setTag.mockReset();
    sentryMocks.setContext.mockReset();
    sentryMocks.withScope.mockClear();
    vi.unstubAllGlobals();
  });

  it("adds X-Request-ID to outgoing requests", async () => {
    sentryMocks.getIdToken.mockResolvedValue("token-123");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiClient.get("/health");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/health"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer token-123",
          "Content-Type": "application/json",
          "X-Request-ID": expect.any(String),
        }),
      }),
    );
  });

  it("records Sentry breadcrumb and captures 5xx API errors", async () => {
    sentryMocks.getIdToken.mockResolvedValue("token-123");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Internal server error" }), {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": "srv-500",
        },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiClient.get("/api/v1/tasks")).rejects.toBeInstanceOf(
      ApiError,
    );

    expect(sentryMocks.addBreadcrumb).toHaveBeenCalledWith(
      expect.objectContaining({
        category: "api",
        data: expect.objectContaining({
          method: "GET",
          path: "/api/v1/tasks",
          request_id: "srv-500",
          status_code: 500,
        }),
      }),
    );
    expect(sentryMocks.withScope).toHaveBeenCalledTimes(1);
    expect(sentryMocks.setTag).toHaveBeenCalledWith("request_id", "srv-500");
    expect(sentryMocks.captureException).toHaveBeenCalledTimes(1);
  });
});
