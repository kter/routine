import { describe, expect, it } from "vitest";
import {
  getSentryRuntimeConfig,
  getTracePropagationTargets,
  parseTracesSampleRate,
} from "./sentryOptions";

describe("parseTracesSampleRate", () => {
  it("keeps valid rates", () => {
    expect(parseTracesSampleRate("0.25")).toBe(0.25);
  });

  it("falls back for invalid rates", () => {
    expect(parseTracesSampleRate("2")).toBe(0.1);
    expect(parseTracesSampleRate("abc")).toBe(0.1);
    expect(parseTracesSampleRate(undefined)).toBe(0.1);
  });
});

describe("getTracePropagationTargets", () => {
  it("includes API proxy and explicit backend targets", () => {
    const targets = getTracePropagationTargets("https://api.example.com");

    expect(targets).toContain("localhost");
    expect(targets).toContain("https://api.example.com");
    expect(
      targets.some(
        (target) => target instanceof RegExp && target.test("/api/tasks"),
      ),
    ).toBe(true);
  });
});

describe("getSentryRuntimeConfig", () => {
  it("returns null when no DSN is configured", () => {
    expect(
      getSentryRuntimeConfig({
        MODE: "development",
      }),
    ).toBeNull();
  });

  it("builds runtime config from env", () => {
    expect(
      getSentryRuntimeConfig({
        MODE: "development",
        VITE_API_BASE_URL: "https://api.example.com",
        VITE_SENTRY_DSN: "https://dsn.example/123",
        VITE_SENTRY_ENVIRONMENT: "staging",
        VITE_SENTRY_TRACES_SAMPLE_RATE: "0.5",
      }),
    ).toMatchObject({
      dsn: "https://dsn.example/123",
      environment: "staging",
      tracesSampleRate: 0.5,
    });
  });
});
