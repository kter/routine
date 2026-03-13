import { useCallback, useEffect, useState } from "react";
import { executionsApi } from "@/lib/api/executions";
import { normalizeApiError } from "@/lib/api/client";
import { useApiResource } from "@/lib/hooks/useApiResource";
import type { Execution, CompleteStepRequest } from "../types";

export function useExecutions() {
  const fetchExecutions = useCallback(() => executionsApi.list(), []);
  const {
    data: executions,
    isLoading,
    error,
    refetch,
  } = useApiResource(fetchExecutions, {
    initialData: [] as Execution[],
    errorMessage: "Failed to fetch executions",
  });

  return { executions, isLoading, error, refetch };
}

export function useExecution(id: string) {
  const fetchExecution = useCallback(async () => executionsApi.get(id), [id]);
  const {
    data: execution,
    isLoading,
    error,
    refetch: fetchExecutionState,
  } = useApiResource<Execution | null>(fetchExecution, {
    initialData: null,
    errorMessage: "Failed to fetch execution",
  });
  const [actionError, setActionError] = useState<Error | null>(null);

  useEffect(() => {
    setActionError(null);
  }, [id]);

  const runAction = useCallback(
    async (action: () => Promise<unknown>) => {
      setActionError(null);
      try {
        await action();
        await fetchExecutionState();
      } catch (err) {
        setActionError(normalizeApiError(err, "Failed to update execution"));
      }
    },
    [fetchExecutionState],
  );

  const completeStep = async (stepId: string, req: CompleteStepRequest) => {
    await runAction(() => executionsApi.completeStep(id, stepId, req));
  };

  const skipStep = async (stepId: string) => {
    await runAction(() => executionsApi.skipStep(id, stepId));
  };

  const completeExecution = async (notes?: string) => {
    await runAction(() => executionsApi.complete(id, { notes }));
  };

  const abandonExecution = async (notes?: string) => {
    await runAction(() => executionsApi.abandon(id, { notes }));
  };

  return {
    execution,
    isLoading,
    error: actionError ?? error,
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
    refetch: fetchExecutionState,
  };
}
