import { Link } from "react-router-dom";
import { useRegisterScreen } from "@/features/auth/hooks/useRegisterScreen";

export function RegisterScreen() {
  const screen = useRegisterScreen();

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30">
      <div className="w-full max-w-sm rounded-lg border bg-card p-8 shadow-sm">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold">RoutineOps</h1>
          <p className="mt-1 text-sm text-muted-foreground">アカウント作成</p>
        </div>

        {screen.step === "signup" && (
          <form
            onSubmit={screen.signUpForm.handleSubmit(screen.onSignUp)}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium">
                メールアドレス
              </label>
              <input
                type="email"
                {...screen.signUpForm.register("email")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {screen.signUpForm.formState.errors.email && (
                <p className="mt-1 text-xs text-destructive">
                  {screen.signUpForm.formState.errors.email.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium">パスワード</label>
              <input
                type="password"
                {...screen.signUpForm.register("password")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {screen.signUpForm.formState.errors.password && (
                <p className="mt-1 text-xs text-destructive">
                  {screen.signUpForm.formState.errors.password.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium">
                パスワード（確認）
              </label>
              <input
                type="password"
                {...screen.signUpForm.register("confirmPassword")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {screen.signUpForm.formState.errors.confirmPassword && (
                <p className="mt-1 text-xs text-destructive">
                  {screen.signUpForm.formState.errors.confirmPassword.message}
                </p>
              )}
            </div>
            {screen.error && (
              <p className="text-sm text-destructive">{screen.error}</p>
            )}
            <button
              type="submit"
              disabled={screen.signUpForm.formState.isSubmitting}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {screen.signUpForm.formState.isSubmitting ? "登録中..." : "登録"}
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
        )}

        {screen.step === "confirm" && (
          <form
            onSubmit={screen.confirmForm.handleSubmit(screen.onConfirm)}
            className="space-y-4"
          >
            <p className="text-sm text-muted-foreground">
              <span className="font-medium">{screen.email}</span>{" "}
              に確認コードを送信しました。
            </p>
            <div>
              <label className="block text-sm font-medium">確認コード</label>
              <input
                type="text"
                inputMode="numeric"
                {...screen.confirmForm.register("code")}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {screen.confirmForm.formState.errors.code && (
                <p className="mt-1 text-xs text-destructive">
                  {screen.confirmForm.formState.errors.code.message}
                </p>
              )}
            </div>
            {screen.error && (
              <p className="text-sm text-destructive">{screen.error}</p>
            )}
            <button
              type="submit"
              disabled={screen.confirmForm.formState.isSubmitting}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {screen.confirmForm.formState.isSubmitting ? "確認中..." : "確認"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
