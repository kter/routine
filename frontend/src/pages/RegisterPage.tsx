import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { signUp, confirmSignUp } from "@/lib/auth/cognito";

const signUpSchema = z
  .object({
    email: z.string().email("有効なメールアドレスを入力してください"),
    password: z
      .string()
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(/[A-Z]/, "大文字を含めてください")
      .regex(/[a-z]/, "小文字を含めてください")
      .regex(/[0-9]/, "数字を含めてください"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "パスワードが一致しません",
    path: ["confirmPassword"],
  });

const confirmSchema = z.object({
  code: z.string().min(1, "確認コードを入力してください"),
});

type SignUpValues = z.infer<typeof signUpSchema>;
type ConfirmValues = z.infer<typeof confirmSchema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<"signup" | "confirm">("signup");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);

  const signUpForm = useForm<SignUpValues>({ resolver: zodResolver(signUpSchema) });
  const confirmForm = useForm<ConfirmValues>({ resolver: zodResolver(confirmSchema) });

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

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30">
      <div className="w-full max-w-sm rounded-lg border bg-card p-8 shadow-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold">RoutineOps</h1>
          <p className="mt-1 text-sm text-muted-foreground">アカウント作成</p>
        </div>

        {step === "signup" && (
          <form onSubmit={signUpForm.handleSubmit(onSignUp)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">メールアドレス</label>
              <input
                type="email"
                {...signUpForm.register("email")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {signUpForm.formState.errors.email && (
                <p className="mt-1 text-xs text-destructive">
                  {signUpForm.formState.errors.email.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium">パスワード</label>
              <input
                type="password"
                {...signUpForm.register("password")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {signUpForm.formState.errors.password && (
                <p className="mt-1 text-xs text-destructive">
                  {signUpForm.formState.errors.password.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium">パスワード（確認）</label>
              <input
                type="password"
                {...signUpForm.register("confirmPassword")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {signUpForm.formState.errors.confirmPassword && (
                <p className="mt-1 text-xs text-destructive">
                  {signUpForm.formState.errors.confirmPassword.message}
                </p>
              )}
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <button
              type="submit"
              disabled={signUpForm.formState.isSubmitting}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {signUpForm.formState.isSubmitting ? "登録中..." : "登録"}
            </button>
            <p className="text-center text-sm text-muted-foreground">
              すでにアカウントをお持ちの方は{" "}
              <Link to="/login" className="text-primary underline-offset-4 hover:underline">
                ログイン
              </Link>
            </p>
          </form>
        )}

        {step === "confirm" && (
          <form onSubmit={confirmForm.handleSubmit(onConfirm)} className="space-y-4">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium">{email}</span> に確認コードを送信しました。
            </p>
            <div>
              <label className="block text-sm font-medium">確認コード</label>
              <input
                type="text"
                inputMode="numeric"
                {...confirmForm.register("code")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {confirmForm.formState.errors.code && (
                <p className="mt-1 text-xs text-destructive">
                  {confirmForm.formState.errors.code.message}
                </p>
              )}
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <button
              type="submit"
              disabled={confirmForm.formState.isSubmitting}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {confirmForm.formState.isSubmitting ? "確認中..." : "確認"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
