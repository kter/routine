import { useNavigate } from "react-router-dom";
import { formatDashboardDateLabel } from "../view-models";
import { useDashboard } from "./useDashboard";
import { useStartExecution } from "@/features/executions/hooks/useExecution";

export function useDashboardScreen() {
  const { data, isLoading, error, refetch } = useDashboard();
  const { startExecution } = useStartExecution();
  const navigate = useNavigate();

  const handleStartExecution = async (taskId: string) => {
    const execution = await startExecution(taskId);
    navigate(`/executions/${execution.id}`);
  };

  return {
    data,
    isLoading,
    error,
    retry: () => refetch(),
    dateLabel: formatDashboardDateLabel(),
    handleStartExecution,
  };
}
