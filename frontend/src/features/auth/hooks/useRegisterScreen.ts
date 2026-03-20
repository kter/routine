import { useState } from "react";
import { getGuestScreenState } from "../view-models";
import { useAuth } from "./useAuth";
import { useRegisterConfirmStep } from "./useRegisterConfirmStep";
import { useRegisterSignUpStep } from "./useRegisterSignUpStep";

export function useRegisterScreen() {
  const { isAuthenticated, isLoading } = useAuth();
  const [step, setStep] = useState<"signup" | "confirm">("signup");
  const [email, setEmail] = useState("");
  const signUpStep = useRegisterSignUpStep({
    onCompleted: (nextEmail) => {
      setEmail(nextEmail);
      setStep("confirm");
    },
  });
  const confirmStep = useRegisterConfirmStep({ email });

  const guestState = getGuestScreenState({ isAuthenticated, isLoading });

  if (guestState.status !== "ready") {
    return guestState;
  }

  return {
    status: "ready" as const,
    step,
    email,
    signUpStep,
    confirmStep,
  };
}
