import { useParams } from "react-router-dom";
import { useExecution } from "./useExecution";

export function useExecutionLogScreen() {
  const { id } = useParams<{ id: string }>();
  const executionId = id ?? "";

  return useExecution(executionId);
}
