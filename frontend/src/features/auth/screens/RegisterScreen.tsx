import { Navigate } from "react-router-dom";
import { AuthPanelHeader } from "@/features/auth/components/AuthPanelHeader";
import { AuthStateScreen } from "@/features/auth/components/AuthStateScreen";
import { AuthScreenFrame } from "@/features/auth/components/AuthScreenFrame";
import { RegisterConfirmForm } from "@/features/auth/components/RegisterConfirmForm";
import { RegisterSignUpForm } from "@/features/auth/components/RegisterSignUpForm";
import { useRegisterScreen } from "@/features/auth/hooks/useRegisterScreen";
import {
  getAuthStateMessage,
  getRegisterScreenHeader,
} from "@/features/auth/view-models";

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
