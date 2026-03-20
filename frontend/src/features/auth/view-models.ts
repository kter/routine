import type { AuthState } from "./types";

export type GuestScreenState =
  | { status: "loading" }
  | { status: "redirect"; to: string }
  | { status: "ready" };

export interface AuthStateMessageViewModel {
  title: string;
  description: string;
}

export interface AuthPanelHeaderViewModel {
  title: string;
  eyebrow: string;
}

export function getGuestScreenState(
  authState: Pick<AuthState, "isLoading" | "isAuthenticated">,
  redirectTo = "/",
): GuestScreenState {
  if (authState.isLoading) {
    return { status: "loading" };
  }

  if (authState.isAuthenticated) {
    return { status: "redirect", to: redirectTo };
  }

  return { status: "ready" };
}

export function getAuthStateMessage(
  kind: "login_loading" | "register_loading" | "protected_loading",
): AuthStateMessageViewModel {
  switch (kind) {
    case "login_loading":
      return {
        title: "認証状態を確認中...",
        description: "セッションの有効性を検証しています。",
      };
    case "register_loading":
      return {
        title: "認証状態を確認中...",
        description: "サインアップ画面を準備しています。",
      };
    case "protected_loading":
      return {
        title: "認証状態を確認中...",
        description: "アクセス権を検証しています。",
      };
  }
}

export function getRegisterScreenHeader(): AuthPanelHeaderViewModel {
  return {
    title: "アカウント作成",
    eyebrow: "Cognito User Registration",
  };
}
