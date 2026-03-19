import { Navigate } from "react-router-dom";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { useLoginScreen } from "@/features/auth/hooks/useLoginScreen";

export function LoginScreen() {
  const screen = useLoginScreen();

  if (screen.status === "loading") {
    return null;
  }

  if (screen.status === "authenticated") {
    return <Navigate to="/" replace />;
  }

  return (
    <AuthScreenFrame>
      <LoginForm />
    </AuthScreenFrame>
  );
}
