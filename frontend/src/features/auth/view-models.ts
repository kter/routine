import type { AuthState } from "./types";

export type GuestScreenState =
  | { status: "loading" }
  | { status: "redirect"; to: string }
  | { status: "ready" };

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
