import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { signUp } from "@/lib/auth/cognito";
import { signUpSchema, type SignUpValues } from "../schemas/register";

interface UseRegisterSignUpStepParams {
  onCompleted: (email: string) => void;
}

export function useRegisterSignUpStep({
  onCompleted,
}: UseRegisterSignUpStepParams) {
  const [error, setError] = useState<string | null>(null);
  const form = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
  });

  const onSubmit = async (data: SignUpValues) => {
    setError(null);
    try {
      await signUp(data.email, data.password);
      onCompleted(data.email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録に失敗しました");
    }
  };

  return {
    form,
    error,
    onSubmit,
  };
}
