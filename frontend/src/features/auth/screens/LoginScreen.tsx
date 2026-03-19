import { Navigate } from "react-router-dom";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { useLoginScreen } from "@/features/auth/hooks/useLoginScreen";

export function LoginScreen() {
  const screen = useLoginScreen();

  if (screen.status === "loading") {
    return (
      <AuthScreenFrame>
        <PageStateMessage
          title="認証状態を確認中..."
          description="セッションの有効性を検証しています。"
          className="flex min-h-40 flex-col items-center justify-center gap-3"
          titleClassName="text-sm"
          descriptionClassName="text-xs text-muted-foreground"
        />
      </AuthScreenFrame>
    );
  }

  if (screen.status === "redirect") {
    return <Navigate to={screen.to} replace />;
  }

  return (
    <AuthScreenFrame>
      <LoginForm />
    </AuthScreenFrame>
  );
}
