import { Navigate } from "react-router-dom";
import {
  AuthPanelHeader,
  AuthScreenFrame,
  AuthStateScreen,
  RegisterConfirmForm,
  RegisterSignUpForm,
} from "../components";
import { useRegisterScreen } from "../hooks";
import { getAuthStateMessage, getRegisterScreenHeader } from "../view-models";

export function RegisterScreen() {
  const screen = useRegisterScreen();
  const loadingMessage = getAuthStateMessage("register_loading");
  const header = getRegisterScreenHeader();

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
      <div>
        <AuthPanelHeader title={header.title} eyebrow={header.eyebrow} />

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
