import { useCallback, useEffect, useState } from "react";
import { executionsApi } from "@/lib/api/executions";
import type { Execution, CompleteStepRequest } from "../types";

export function useExecutions() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchExecutions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await executionsApi.list();
      setExecutions(data);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch executions"),
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
  }, []);

  return { executions, isLoading, error, refetch: fetchExecutions };
}

export function useExecution(id: string) {
  const [execution, setExecution] = useState<Execution | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchExecution = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await executionsApi.get(id);
      setExecution(data);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch execution"),
      );
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void fetchExecution();
  }, [fetchExecution]);

  const completeStep = async (stepId: string, req: CompleteStepRequest) => {
    await executionsApi.completeStep(id, stepId, req);
    await fetchExecution();
  };

  const skipStep = async (stepId: string) => {
    await executionsApi.skipStep(id, stepId);
    await fetchExecution();
  };

  const completeExecution = async (notes?: string) => {
    await executionsApi.complete(id, { notes });
    await fetchExecution();
  };

  const abandonExecution = async (notes?: string) => {
    await executionsApi.abandon(id, { notes });
    await fetchExecution();
  };

  return {
    execution,
    isLoading,
    error,
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
    refetch: fetchExecution,
  };
}
