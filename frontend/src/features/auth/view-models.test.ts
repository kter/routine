import { describe, expect, it } from "vitest";
import { getGuestScreenState } from "./view-models";

describe("getGuestScreenState", () => {
  it("returns loading while auth state is resolving", () => {
    expect(
      getGuestScreenState({
        isLoading: true,
        isAuthenticated: false,
      }),
    ).toEqual({ status: "loading" });
  });

  it("redirects authenticated users to the requested route", () => {
    expect(
      getGuestScreenState(
        {
          isLoading: false,
          isAuthenticated: true,
        },
        "/tasks",
      ),
    ).toEqual({ status: "redirect", to: "/tasks" });
  });

  it("returns ready for anonymous users after auth state resolves", () => {
    expect(
      getGuestScreenState({
        isLoading: false,
        isAuthenticated: false,
      }),
    ).toEqual({ status: "ready" });
  });
});
