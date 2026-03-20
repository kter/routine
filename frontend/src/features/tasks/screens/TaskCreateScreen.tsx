import { TaskForm } from "../components";
import { useTaskCreateScreen } from "../hooks";

export function TaskCreateScreen() {
  const { handleSubmit } = useTaskCreateScreen();

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">タスクを作成</h1>
      <div className="rounded-lg border bg-card p-6">
        <TaskForm onSubmit={handleSubmit} submitLabel="作成" />
      </div>
    </div>
  );
}
