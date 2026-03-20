import { useParams } from "react-router-dom";
import { getExecutionScreenTitle } from "../view-models";
import { useExecution } from "./useExecution";

export function useExecutionScreen() {
  const { id } = useParams<{ id: string }>();
  const executionId = id ?? "";
  const {
    execution,
    isLoading,
    error,
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
  } = useExecution(executionId);

  if (isLoading) {
    return { status: "loading" as const };
  }

  if (error || !execution) {
    return { status: "not_found" as const };
  }

  return {
    status: "ready" as const,
    execution,
    title: getExecutionScreenTitle(execution),
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
  };
}
