import { Navigate } from "react-router-dom";
import { AuthStateScreen } from "@/features/auth/components/AuthStateScreen";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { useLoginScreen } from "@/features/auth/hooks/useLoginScreen";

export function LoginScreen() {
  const screen = useLoginScreen();

  if (screen.status === "loading") {
    return (
      <AuthStateScreen
        title="認証状態を確認中..."
        description="セッションの有効性を検証しています。"
      />
    );
  }

  if (screen.status === "redirect") {
    return <Navigate to={screen.to} replace />;
  }

  return (
    <AuthScreenFrame>
      <LoginForm
        form={screen.form}
        error={screen.error}
        onSubmit={screen.onSubmit}
      />
    </AuthScreenFrame>
  );
}
