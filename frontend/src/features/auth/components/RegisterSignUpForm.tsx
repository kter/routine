import { Link } from "react-router-dom";
import type { UseFormReturn } from "react-hook-form";
import type { SignUpValues } from "../schemas/register";

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
      <div>
        <label className="block text-sm font-medium">メールアドレス</label>
        <input
          type="email"
          {...form.register("email")}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        {form.formState.errors.email && (
          <p className="mt-1 text-xs text-destructive">
            {form.formState.errors.email.message}
          </p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium">パスワード</label>
        <input
          type="password"
          {...form.register("password")}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        {form.formState.errors.password && (
          <p className="mt-1 text-xs text-destructive">
            {form.formState.errors.password.message}
          </p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium">パスワード（確認）</label>
        <input
          type="password"
          {...form.register("confirmPassword")}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        {form.formState.errors.confirmPassword && (
          <p className="mt-1 text-xs text-destructive">
            {form.formState.errors.confirmPassword.message}
          </p>
        )}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <button
        type="submit"
        disabled={form.formState.isSubmitting}
        className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {form.formState.isSubmitting ? "登録中..." : "登録"}
      </button>
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
