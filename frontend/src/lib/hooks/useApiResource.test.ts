import { describe, expect, it } from "vitest";
import { shouldApplyResourceResult } from "./useApiResource";

describe("shouldApplyResourceResult", () => {
  it("applies the latest request result for the current generation", () => {
    expect(
      shouldApplyResourceResult(
        { generation: 2, requestId: 4 },
        { currentGeneration: 2, latestRequestId: 4 },
      ),
    ).toBe(true);
  });

  it("rejects stale results from an older request id", () => {
    expect(
      shouldApplyResourceResult(
        { generation: 2, requestId: 3 },
        { currentGeneration: 2, latestRequestId: 4 },
      ),
    ).toBe(false);
  });

  it("rejects stale results from an older fetcher generation", () => {
    expect(
      shouldApplyResourceResult(
        { generation: 1, requestId: 7 },
        { currentGeneration: 2, latestRequestId: 7 },
      ),
    ).toBe(false);
  });
});
