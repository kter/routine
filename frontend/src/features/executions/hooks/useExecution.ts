import {
  type QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { executionsApi } from "@/lib/api/executions";
import { normalizeApiError } from "@/lib/api/client";
import { getQueryError } from "@/lib/query/queryError";
import { queryKeys } from "@/lib/query/queryKeys";
import type { CompleteStepInput, Execution } from "../types";

export function useExecutions() {
  const query = useQuery<Execution[]>({
    queryKey: queryKeys.executions.all,
    queryFn: executionsApi.list,
  });

  return {
    executions: query.data ?? [],
    isLoading: query.isPending,
    error: getQueryError(query.error, "Failed to fetch executions"),
    refetch: query.refetch,
  };
}

export function getExecutionHookError(error: Error | null): Error | null {
  return error;
}

async function invalidateExecutionQueries(
  queryClient: QueryClient,
  id?: string,
) {
  const invalidations = [
    queryClient.invalidateQueries({ queryKey: queryKeys.executions.all }),
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
  ];

  if (id) {
    invalidations.push(
      queryClient.invalidateQueries({
        queryKey: queryKeys.executions.detail(id),
      }),
    );
  }

  await Promise.all(invalidations);
}

export function useExecution(id: string) {
  const queryClient = useQueryClient();
  const query = useQuery<Execution>({
    queryKey: queryKeys.executions.detail(id),
    queryFn: () => executionsApi.get(id),
    enabled: Boolean(id),
  });
  const [actionError, setActionError] = useState<Error | null>(null);
  const completeStepMutation = useMutation({
    mutationFn: ({ stepId, req }: { stepId: string; req: CompleteStepInput }) =>
      executionsApi.completeStep(id, stepId, req),
  });
  const skipStepMutation = useMutation({
    mutationFn: (stepId: string) => executionsApi.skipStep(id, stepId),
  });
  const completeExecutionMutation = useMutation({
    mutationFn: (notes?: string) => executionsApi.complete(id, { notes }),
  });
  const abandonExecutionMutation = useMutation({
    mutationFn: (notes?: string) => executionsApi.abandon(id, { notes }),
  });

  useEffect(() => {
    setActionError(null);
  }, [id]);

  const runAction = async (action: () => Promise<unknown>) => {
    setActionError(null);
    try {
      await action();
      await invalidateExecutionQueries(queryClient, id);
    } catch (err) {
      setActionError(normalizeApiError(err, "Failed to update execution"));
    }
  };

  const completeStep = async (stepId: string, req: CompleteStepInput) => {
    await runAction(() => completeStepMutation.mutateAsync({ stepId, req }));
  };

  const skipStep = async (stepId: string) => {
    await runAction(() => skipStepMutation.mutateAsync(stepId));
  };

  const completeExecution = async (notes?: string) => {
    await runAction(() => completeExecutionMutation.mutateAsync(notes));
  };

  const abandonExecution = async (notes?: string) => {
    await runAction(() => abandonExecutionMutation.mutateAsync(notes));
  };

  return {
    execution: query.data ?? null,
    isLoading: query.isPending,
    error: getExecutionHookError(
      getQueryError(query.error, "Failed to fetch execution"),
    ),
    actionError,
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
    refetch: query.refetch,
  };
}

export function useStartExecution() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<Error | null>(null);
  const mutation = useMutation({
    mutationFn: (taskId: string) => executionsApi.start({ taskId }),
  });

  const startExecution = async (taskId: string) => {
    setError(null);
    try {
      const execution = await mutation.mutateAsync(taskId);
      queryClient.setQueryData(
        queryKeys.executions.detail(execution.id),
        execution,
      );
      await invalidateExecutionQueries(queryClient);
      return execution;
    } catch (err) {
      const normalizedError = normalizeApiError(
        err,
        "Failed to start execution",
      );
      setError(normalizedError);
      throw normalizedError;
    }
  };

  return {
    startExecution,
    isLoading: mutation.isPending,
    error,
  };
}
