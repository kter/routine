import { describe, expect, it } from "vitest";
import { getExecutionHookError } from "./useExecution";

describe("getExecutionHookError", () => {
  it("returns fetch errors for page-level handling", () => {
    const fetchError = new Error("failed to fetch");

    expect(getExecutionHookError(fetchError)).toBe(fetchError);
  });

  it("does not synthesize page-level errors for mutation failures", () => {
    expect(getExecutionHookError(null)).toBeNull();
  });
});
