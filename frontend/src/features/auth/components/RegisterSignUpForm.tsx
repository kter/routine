import { Link } from "react-router-dom";
import type { UseFormReturn } from "react-hook-form";
import type { SignUpValues } from "../schemas/register";
import { AuthFormError } from "./AuthFormError";
import { AuthFormField } from "./AuthFormField";
import { AuthSubmitButton } from "./AuthSubmitButton";

interface RegisterSignUpFormProps {
  form: UseFormReturn<SignUpValues>;
  error: string | null;
  onSubmit: (data: SignUpValues) => Promise<void>;
}

export function RegisterSignUpForm({
  form,
  error,
  onSubmit,
}: RegisterSignUpFormProps) {
  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <AuthFormField
        label="メールアドレス"
        type="email"
        error={form.formState.errors.email?.message}
        {...form.register("email")}
      />
      <AuthFormField
        label="パスワード"
        type="password"
        error={form.formState.errors.password?.message}
        {...form.register("password")}
      />
      <AuthFormField
        label="パスワード（確認）"
        type="password"
        error={form.formState.errors.confirmPassword?.message}
        {...form.register("confirmPassword")}
      />
      <AuthFormError message={error} />
      <AuthSubmitButton
        idleLabel="登録"
        submittingLabel="登録中..."
        isSubmitting={form.formState.isSubmitting}
      />
      <p className="text-center text-sm text-muted-foreground">
        すでにアカウントをお持ちの方は{" "}
        <Link
          to="/login"
          className="text-primary underline-offset-4 hover:underline"
        >
          ログイン
        </Link>
      </p>
    </form>
  );
}
