import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useAuth } from "./useAuth";
import { loginSchema, type LoginValues } from "../schemas/login";
import { getGuestScreenState } from "../view-models";
import { signIn } from "@/lib/auth/cognito";

export function useLoginScreen() {
  const { isAuthenticated, isLoading, refreshUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  });

  const guestState = getGuestScreenState({ isAuthenticated, isLoading });

  if (guestState.status !== "ready") {
    return guestState;
  }

  const onSubmit = async (data: LoginValues) => {
    setError(null);
    try {
      await signIn(data.email, data.password);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    }
  };

  return {
    status: "ready" as const,
    form,
    error,
    onSubmit,
  };
}
