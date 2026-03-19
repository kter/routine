import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useStartExecution } from "@/features/executions/hooks/useExecution";
import { useTaskMutations } from "./useTaskMutations";
import { useTask } from "./useTasks";

export function useTaskDetailScreen() {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "";
  const navigate = useNavigate();
  const { task, isLoading, error } = useTask(taskId);
  const { deleteTask } = useTaskMutations();
  const { startExecution } = useStartExecution();
  const [showDelete, setShowDelete] = useState(false);

  const handleDelete = async () => {
    await deleteTask(taskId);
    navigate("/tasks");
  };

  const handleStartExecution = async () => {
    const execution = await startExecution(taskId);
    navigate(`/executions/${execution.id}`);
  };

  return {
    taskId,
    task: task ?? null,
    isLoading,
    error,
    showDelete,
    openDeleteDialog: () => setShowDelete(true),
    closeDeleteDialog: () => setShowDelete(false),
    handleDelete,
    handleStartExecution,
  };
}
