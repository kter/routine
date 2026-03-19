import { useNavigate, useParams } from "react-router-dom";
import type { TaskInput } from "@/features/tasks/types";
import { toTaskFormViewModel } from "../view-models";
import { useTaskMutations } from "./useTaskMutations";
import { useTask } from "./useTasks";

export function useTaskEditScreen() {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "";
  const navigate = useNavigate();
  const { task, isLoading, error } = useTask(taskId);
  const { updateTask } = useTaskMutations();

  const handleSubmit = async (data: TaskInput) => {
    await updateTask(taskId, data);
    navigate(`/tasks/${taskId}`);
  };

  return {
    task: task ?? null,
    taskId,
    isLoading,
    error,
    form: task ? toTaskFormViewModel(task) : null,
    handleSubmit,
  };
}
