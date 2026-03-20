import { Link } from "react-router-dom";
import type { UseFormReturn } from "react-hook-form";
import type { LoginValues } from "../schemas/login";
import { AuthFormError } from "./AuthFormError";
import { AuthFormField } from "./AuthFormField";
import { AuthSubmitButton } from "./AuthSubmitButton";

interface LoginFormProps {
  form: UseFormReturn<LoginValues>;
  error: string | null;
  onSubmit: (data: LoginValues) => Promise<void>;
}

export function LoginForm({ form, error, onSubmit }: LoginFormProps) {
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
      <AuthFormError message={error} />
      <AuthSubmitButton
        idleLabel="ログイン"
        submittingLabel="ログイン中..."
        isSubmitting={form.formState.isSubmitting}
      />
      <p className="text-center text-sm text-muted-foreground">
        アカウント作成は{" "}
        <Link
          to="/register"
          className="text-primary underline-offset-4 hover:underline"
        >
          こちら
        </Link>
      </p>
    </form>
  );
}
