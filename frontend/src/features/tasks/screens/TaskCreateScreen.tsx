import { useNavigate } from "react-router-dom";
import { TaskForm } from "@/features/tasks/components/TaskForm";
import { useTaskMutations } from "@/features/tasks/hooks/useTaskMutations";
import type { TaskInput } from "@/features/tasks/types";

export function TaskCreateScreen() {
  const navigate = useNavigate();
  const { createTask } = useTaskMutations();

  const handleSubmit = async (data: TaskInput) => {
    const task = await createTask(data);
    navigate(`/tasks/${task.id}`);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">タスクを作成</h1>
      <div className="rounded-lg border bg-card p-6">
        <TaskForm onSubmit={handleSubmit} submitLabel="作成" />
      </div>
    </div>
  );
}
