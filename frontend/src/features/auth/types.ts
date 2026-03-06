export interface AuthUser {
  sub: string;
  email: string;
  tenantId: string;
}

export interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}
