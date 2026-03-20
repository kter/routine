import { useParams } from "react-router-dom";
import { toExecutionLogViewModel } from "../view-models";
import { useExecution } from "./useExecution";

export function useExecutionLogScreen() {
  const { id } = useParams<{ id: string }>();
  const executionId = id ?? "";
  const { execution, isLoading, error } = useExecution(executionId);

  if (isLoading) {
    return { status: "loading" as const };
  }

  if (error || !execution) {
    return { status: "not_found" as const };
  }

  return {
    status: "ready" as const,
    viewModel: toExecutionLogViewModel(execution),
    execution,
  };
}
