import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { confirmSignUp } from "@/lib/auth/cognito";
import { confirmSchema, type ConfirmValues } from "../schemas/register";

interface UseRegisterConfirmStepParams {
  email: string;
}

export function useRegisterConfirmStep({
  email,
}: UseRegisterConfirmStepParams) {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const form = useForm<ConfirmValues>({
    resolver: zodResolver(confirmSchema),
  });

  const onSubmit = async (data: ConfirmValues) => {
    setError(null);
    try {
      await confirmSignUp(email, data.code);
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "確認に失敗しました");
    }
  };

  return {
    form,
    error,
    onSubmit,
  };
}
