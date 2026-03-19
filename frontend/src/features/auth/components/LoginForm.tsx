import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { signIn } from "@/lib/auth/cognito";
import { useAuth } from "../hooks/useAuth";
import { AuthFormError } from "./AuthFormError";
import { AuthFormField } from "./AuthFormField";
import { AuthSubmitButton } from "./AuthSubmitButton";

const schema = z.object({
  email: z.string().email("有効なメールアドレスを入力してください"),
  password: z.string().min(8, "パスワードは8文字以上で入力してください"),
});

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const [error, setError] = useState<string | null>(null);
  const { refreshUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormValues) => {
    setError(null);
    try {
      await signIn(data.email, data.password);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <AuthFormField
        label="メールアドレス"
        type="email"
        error={errors.email?.message}
        {...register("email")}
      />
      <AuthFormField
        label="パスワード"
        type="password"
        error={errors.password?.message}
        {...register("password")}
      />
      <AuthFormError message={error} />
      <AuthSubmitButton
        idleLabel="ログイン"
        submittingLabel="ログイン中..."
        isSubmitting={isSubmitting}
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
