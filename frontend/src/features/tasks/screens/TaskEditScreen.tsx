import { TaskForm } from "@/features/tasks/components/TaskForm";
import { useTaskEditScreen } from "@/features/tasks/hooks/useTaskEditScreen";

export function TaskEditScreen() {
  const { task, isLoading, form, handleSubmit } = useTaskEditScreen();

  if (isLoading)
    return <div className="text-sm text-muted-foreground">読み込み中...</div>;
  if (!task)
    return (
      <div className="text-sm text-destructive">タスクが見つかりません</div>
    );

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">タスクを編集</h1>
      <div className="rounded-lg border bg-card p-6">
        <TaskForm
          defaultValues={form?.defaultValues}
          defaultSteps={form?.defaultSteps}
          onSubmit={handleSubmit}
          submitLabel="保存"
        />
      </div>
    </div>
  );
}
