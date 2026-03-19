import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import {
  confirmSchema,
  signUpSchema,
  type ConfirmValues,
  type SignUpValues,
} from "../schemas/register";
import { confirmSignUp, signUp } from "@/lib/auth/cognito";

export function useRegisterScreen() {
  const navigate = useNavigate();
  const [step, setStep] = useState<"signup" | "confirm">("signup");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);

  const signUpForm = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
  });
  const confirmForm = useForm<ConfirmValues>({
    resolver: zodResolver(confirmSchema),
  });

  const onSignUp = async (data: SignUpValues) => {
    setError(null);
    try {
      await signUp(data.email, data.password);
      setEmail(data.email);
      setStep("confirm");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録に失敗しました");
    }
  };

  const onConfirm = async (data: ConfirmValues) => {
    setError(null);
    try {
      await confirmSignUp(email, data.code);
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "確認に失敗しました");
    }
  };

  return {
    step,
    email,
    error,
    signUpForm,
    confirmForm,
    onSignUp,
    onConfirm,
  };
}
