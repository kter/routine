import { RegisterConfirmForm } from "@/features/auth/components/RegisterConfirmForm";
import { RegisterSignUpForm } from "@/features/auth/components/RegisterSignUpForm";
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
          <RegisterSignUpForm
            form={screen.signUpForm}
            error={screen.error}
            onSubmit={screen.onSignUp}
          />
        )}

        {screen.step === "confirm" && (
          <RegisterConfirmForm
            email={screen.email}
            error={screen.error}
            form={screen.confirmForm}
            onSubmit={screen.onConfirm}
          />
        )}
      </div>
    </div>
  );
}
