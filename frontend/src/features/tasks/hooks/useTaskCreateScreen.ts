import { useNavigate } from "react-router-dom";
import type { TaskInput } from "@/features/tasks/types";
import { useTaskMutations } from "./useTaskMutations";

export function useTaskCreateScreen() {
  const navigate = useNavigate();
  const { createTask } = useTaskMutations();

  const handleSubmit = async (data: TaskInput) => {
    const task = await createTask(data);
    navigate(`/tasks/${task.id}`);
  };

  return {
    handleSubmit,
  };
}
