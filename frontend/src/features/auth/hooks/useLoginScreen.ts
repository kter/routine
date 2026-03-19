import { useAuth } from "./useAuth";

export function useLoginScreen() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return { status: "loading" as const };
  }

  if (isAuthenticated) {
    return { status: "authenticated" as const };
  }

  return { status: "ready" as const };
}
