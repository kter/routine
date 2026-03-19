import { describe, expect, it } from "vitest";
import {
  getAuthStateMessage,
  getGuestScreenState,
  getRegisterScreenHeader,
} from "./view-models";

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

describe("getAuthStateMessage", () => {
  it("returns the protected route loading copy", () => {
    expect(getAuthStateMessage("protected_loading")).toEqual({
      title: "認証状態を確認中...",
      description: "アクセス権を検証しています。",
    });
  });
});

describe("getRegisterScreenHeader", () => {
  it("returns the register heading copy", () => {
    expect(getRegisterScreenHeader()).toEqual({
      title: "アカウント作成",
      eyebrow: "Cognito User Registration",
    });
  });
});
