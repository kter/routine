import { useExecutions } from "./useExecution";

export function useExecutionListScreen() {
  const { executions, isLoading, error, refetch } = useExecutions();

  if (isLoading) {
    return { status: "loading" as const };
  }

  if (error) {
    return {
      status: "error" as const,
      retry: () => refetch(),
    };
  }

  return {
    status: "ready" as const,
    executions,
    recordsLabel: `${executions.length} records`,
  };
}
