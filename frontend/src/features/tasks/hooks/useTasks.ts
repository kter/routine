import { useQuery } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api/tasks";
import { getQueryError } from "@/lib/query/queryError";
import { queryKeys } from "@/lib/query/queryKeys";
import type { Task } from "../types";

export function useTasks() {
  const query = useQuery<Task[]>({
    queryKey: queryKeys.tasks.all,
    queryFn: tasksApi.list,
  });

  return {
    tasks: query.data ?? [],
    isLoading: query.isPending,
    error: getQueryError(query.error, "Failed to fetch tasks"),
    refetch: query.refetch,
  };
}

export function useTask(id: string) {
  const query = useQuery<Task>({
    queryKey: queryKeys.tasks.detail(id),
    queryFn: () => tasksApi.get(id),
    enabled: Boolean(id),
  });

  return {
    task: query.data ?? null,
    isLoading: query.isPending,
    error: getQueryError(query.error, "Failed to fetch task"),
  };
}
