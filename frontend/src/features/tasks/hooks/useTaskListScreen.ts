import { useTasks } from "./useTasks";

export function useTaskListScreen() {
  const { tasks, isLoading, error, refetch } = useTasks();

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
    tasks,
  };
}
