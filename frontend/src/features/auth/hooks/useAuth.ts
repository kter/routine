import { useAuthContext } from "../context/useAuthContext";

export function useAuth() {
  return useAuthContext();
}
