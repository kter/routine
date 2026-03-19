import { useAuth } from "./useAuth";
import { getGuestScreenState } from "../view-models";

export function useLoginScreen() {
  const { isAuthenticated, isLoading } = useAuth();

  return getGuestScreenState({ isAuthenticated, isLoading });
}
