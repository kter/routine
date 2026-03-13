import { useCallback } from "react";
import { tasksApi } from "@/lib/api/tasks";
import { useApiResource } from "@/lib/hooks/useApiResource";
import type { Task } from "../types";

export function useTasks() {
  const fetchTasks = useCallback(() => tasksApi.list(), []);
  const {
    data: tasks,
    isLoading,
    error,
    refetch,
  } = useApiResource(fetchTasks, {
    initialData: [] as Task[],
    errorMessage: "Failed to fetch tasks",
  });

  return { tasks, isLoading, error, refetch };
}

export function useTask(id: string) {
  const fetchTask = useCallback(async () => tasksApi.get(id), [id]);
  const {
    data: task,
    isLoading,
    error,
  } = useApiResource<Task | null>(fetchTask, {
    initialData: null,
    errorMessage: "Failed to fetch task",
  });

  return { task, isLoading, error };
}
