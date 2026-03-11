import { createContext, useEffect, useState, type ReactNode } from "react";
import { getCurrentUser, signOut as amplifySignOut } from "@/lib/auth/cognito";
import type { AuthState } from "../types";

interface AuthContextValue extends AuthState {
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  const refreshUser = async () => {
    try {
      const user = await getCurrentUser();
      setState({ user, isLoading: false, isAuthenticated: true });
    } catch {
      setState({ user: null, isLoading: false, isAuthenticated: false });
    }
  };

  const signOut = async () => {
    await amplifySignOut();
    setState({ user: null, isLoading: false, isAuthenticated: false });
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}
export { AuthContext };
