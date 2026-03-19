import { Navigate } from "react-router-dom";
import { AuthStateScreen } from "@/features/auth/components/AuthStateScreen";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { RegisterConfirmForm } from "@/features/auth/components/RegisterConfirmForm";
import { RegisterSignUpForm } from "@/features/auth/components/RegisterSignUpForm";
import { useRegisterScreen } from "@/features/auth/hooks/useRegisterScreen";

export function RegisterScreen() {
  const screen = useRegisterScreen();

  if (screen.status === "loading") {
    return (
      <AuthStateScreen
        title="認証状態を確認中..."
        description="サインアップ画面を準備しています。"
      />
    );
  }

  if (screen.status === "redirect") {
    return <Navigate to={screen.to} replace />;
  }

  return (
    <AuthScreenFrame>
      <div>
        <div className="mb-6 text-center">
          <h2
            className="font-brand text-lg tracking-tight"
            style={{ color: "hsl(210 20% 90%)", fontWeight: 700 }}
          >
            アカウント作成
          </h2>
          <p
            className="mt-1 font-mono-data text-[11px] tracking-wide"
            style={{ color: "hsl(215 16% 38%)" }}
          >
            Cognito User Registration
          </p>
        </div>

        {screen.step === "signup" && (
          <RegisterSignUpForm
            form={screen.signUpStep.form}
            error={screen.signUpStep.error}
            onSubmit={screen.signUpStep.onSubmit}
          />
        )}

        {screen.step === "confirm" && (
          <RegisterConfirmForm
            email={screen.email}
            error={screen.confirmStep.error}
            form={screen.confirmStep.form}
            onSubmit={screen.confirmStep.onSubmit}
          />
        )}
      </div>
    </AuthScreenFrame>
  );
}
