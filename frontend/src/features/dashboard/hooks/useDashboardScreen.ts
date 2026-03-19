import { useNavigate } from "react-router-dom";
import { useStartExecution } from "@/features/executions";
import { formatDashboardDateLabel } from "../view-models";
import { useDashboard } from "./useDashboard";

export function useDashboardScreen() {
  const { data, isLoading, error, refetch } = useDashboard();
  const { startExecution } = useStartExecution();
  const navigate = useNavigate();

  const handleStartExecution = async (taskId: string) => {
    const execution = await startExecution(taskId);
    navigate(`/executions/${execution.id}`);
  };

  if (isLoading) {
    return { status: "loading" as const };
  }

  if (error || !data) {
    return {
      status: "error" as const,
      retry: () => refetch(),
    };
  }

  return {
    status: "ready" as const,
    data,
    dateLabel: formatDashboardDateLabel(),
    handleStartExecution,
  };
}
