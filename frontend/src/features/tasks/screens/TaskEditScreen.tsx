import { PageStateMessage } from "@/components/common/PageStateMessage";
import { TaskForm } from "@/features/tasks/components/TaskForm";
import { useTaskEditScreen } from "@/features/tasks/hooks/useTaskEditScreen";

export function TaskEditScreen() {
  const screen = useTaskEditScreen();

  if (screen.status === "loading")
    return (
      <PageStateMessage
        title="読み込み中..."
        className="flex h-32 items-center"
        titleClassName="text-sm text-muted-foreground"
      />
    );
  if (screen.status === "not_found")
    return (
      <PageStateMessage
        title="タスクが見つかりません"
        className="flex h-32 items-center"
        titleClassName="text-sm text-destructive"
      />
    );

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">タスクを編集</h1>
      <div className="rounded-lg border bg-card p-6">
        <TaskForm
          defaultValues={screen.form.defaultValues}
          defaultSteps={screen.form.defaultSteps}
          onSubmit={screen.handleSubmit}
          submitLabel="保存"
        />
      </div>
    </div>
  );
}
