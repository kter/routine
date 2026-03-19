import { Navigate } from "react-router-dom";
import { AuthScreenFrame, AuthStateScreen, LoginForm } from "../components";
import { useLoginScreen } from "../hooks";
import { getAuthStateMessage } from "../view-models";

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
