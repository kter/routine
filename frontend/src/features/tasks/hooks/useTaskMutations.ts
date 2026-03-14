import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { normalizeApiError } from "@/lib/api/client";
import { tasksApi } from "@/lib/api/tasks";
import { queryKeys } from "@/lib/query/queryKeys";
import type { CreateTaskRequest, UpdateTaskRequest } from "../types";

export function useTaskMutations() {
  const queryClient = useQueryClient();
  const [error, setError] = useState<Error | null>(null);
  const createMutation = useMutation({
    mutationFn: tasksApi.create,
    onSuccess: async (task) => {
      queryClient.setQueryData(queryKeys.tasks.detail(task.id), task);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
      ]);
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTaskRequest }) =>
      tasksApi.update(id, data),
    onSuccess: async (task) => {
      queryClient.setQueryData(queryKeys.tasks.detail(task.id), task);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
      ]);
    },
  });
  const deleteMutation = useMutation({
    mutationFn: tasksApi.delete,
    onSuccess: async (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.tasks.detail(id) });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
      ]);
    },
  });

  const createTask = async (data: CreateTaskRequest) => {
    setError(null);
    try {
      return await createMutation.mutateAsync(data);
    } catch (err) {
      const e = normalizeApiError(err, "Failed to create task");
      setError(e);
      throw e;
    }
  };

  const updateTask = async (id: string, data: UpdateTaskRequest) => {
    setError(null);
    try {
      return await updateMutation.mutateAsync({ id, data });
    } catch (err) {
      const e = normalizeApiError(err, "Failed to update task");
      setError(e);
      throw e;
    }
  };

  const deleteTask = async (id: string) => {
    setError(null);
    try {
      await deleteMutation.mutateAsync(id);
    } catch (err) {
      const e = normalizeApiError(err, "Failed to delete task");
      setError(e);
      throw e;
    }
  };

  return {
    createTask,
    updateTask,
    deleteTask,
    isLoading:
      createMutation.isPending ||
      updateMutation.isPending ||
      deleteMutation.isPending,
    error,
  };
}
