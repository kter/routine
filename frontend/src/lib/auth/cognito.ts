import { Amplify } from "aws-amplify";
import {
  signIn as amplifySignIn,
  signOut as amplifySignOut,
  signUp as amplifySignUp,
  confirmSignUp as amplifyConfirmSignUp,
  getCurrentUser as amplifyGetCurrentUser,
  fetchAuthSession,
} from "aws-amplify/auth";
import type { AuthUser } from "@/features/auth/types";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID as string,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID as string,
    },
  },
});

export async function signIn(email: string, password: string): Promise<void> {
  await amplifySignIn({ username: email, password });
}

export async function signUp(email: string, password: string): Promise<void> {
  await amplifySignUp({ username: email, password });
}

export async function confirmSignUp(
  email: string,
  code: string,
): Promise<void> {
  await amplifyConfirmSignUp({ username: email, confirmationCode: code });
}

export async function signOut(): Promise<void> {
  await amplifySignOut();
}

export async function getCurrentUser(): Promise<AuthUser> {
  const cognitoUser = await amplifyGetCurrentUser();
  const session = await fetchAuthSession();
  const idToken = session.tokens?.idToken;

  if (!idToken) throw new Error("No auth session");

  const payload = idToken.payload as Record<string, unknown>;
  const tenantId = (payload["custom:tenant_id"] as string) ?? "";

  return {
    sub: cognitoUser.userId,
    email: cognitoUser.signInDetails?.loginId ?? "",
    tenantId,
  };
}

export async function getIdToken(): Promise<string> {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken?.toString();
  if (!token) throw new Error("Not authenticated");
  return token;
}
