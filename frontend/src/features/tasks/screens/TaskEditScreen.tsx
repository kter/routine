import { useNavigate, useParams } from "react-router-dom";
import { TaskForm } from "@/features/tasks/components/TaskForm";
import { useTaskMutations } from "@/features/tasks/hooks/useTaskMutations";
import { useTask } from "@/features/tasks/hooks/useTasks";
import type { TaskInput } from "@/features/tasks/types";

export function TaskEditScreen() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { task, isLoading } = useTask(id!);
  const { updateTask } = useTaskMutations();

  const handleSubmit = async (data: TaskInput) => {
    await updateTask(id!, data);
    navigate(`/tasks/${id}`);
  };

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
          defaultValues={{
            title: task.title,
            description: task.description,
            cronExpression: task.cronExpression,
            timezone: task.timezone,
            estimatedMinutes: task.estimatedMinutes,
            tags: task.tags.join(", "),
          }}
          defaultSteps={
            task.steps?.map((s) => ({
              position: s.position,
              title: s.title,
              instruction: s.instruction,
              evidenceType: s.evidenceType,
              isRequired: s.isRequired,
            })) ?? []
          }
          onSubmit={handleSubmit}
          submitLabel="保存"
        />
      </div>
    </div>
  );
}
