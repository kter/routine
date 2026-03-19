import { Navigate } from "react-router-dom";
import { AuthStateScreen } from "@/features/auth/components/AuthStateScreen";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { useLoginScreen } from "@/features/auth/hooks/useLoginScreen";
import { getAuthStateMessage } from "@/features/auth/view-models";

export function LoginScreen() {
  const screen = useLoginScreen();
  const loadingMessage = getAuthStateMessage("login_loading");

  if (screen.status === "loading") {
    return (
      <AuthStateScreen
        title={loadingMessage.title}
        description={loadingMessage.description}
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
