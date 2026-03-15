import { Link, useNavigate, useParams } from "react-router-dom";
import { Edit, Play, Trash2 } from "lucide-react";
import { useTask } from "@/features/tasks/hooks/useTasks";
import { useTaskMutations } from "@/features/tasks/hooks/useTaskMutations";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useStartExecution } from "@/features/executions/hooks/useExecution";
import { formatCron } from "@/lib/utils";
import { useState } from "react";

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { task, isLoading, error } = useTask(id!);
  const { deleteTask } = useTaskMutations();
  const { startExecution } = useStartExecution();
  const [showDelete, setShowDelete] = useState(false);

  const handleDelete = async () => {
    await deleteTask(id!);
    navigate("/tasks");
  };

  const handleStartExecution = async () => {
    const execution = await startExecution(id!);
    navigate(`/executions/${execution.id}`);
  };

  if (isLoading)
    return <div className="text-sm text-muted-foreground">読み込み中...</div>;
  if (error || !task)
    return (
      <div className="text-sm text-destructive">タスクが見つかりません</div>
    );

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">{task.title}</h1>
          <div className="mt-1 flex items-center gap-2">
            <StatusBadge status={task.isActive ? "completed" : "abandoned"} />
            <span className="text-sm text-muted-foreground">
              {formatCron(task.cronExpression)}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleStartExecution}
            className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground"
          >
            <Play className="h-4 w-4" />
            実行
          </button>
          <Link
            to={`/tasks/${id}/edit`}
            className="flex items-center gap-1.5 rounded-md border px-3 py-2 text-sm hover:bg-accent"
          >
            <Edit className="h-4 w-4" />
            編集
          </Link>
          <button
            onClick={() => setShowDelete(true)}
            className="flex items-center gap-1.5 rounded-md border border-destructive px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {task.description && (
        <div className="rounded-lg border bg-card p-4">
          <MarkdownRenderer content={task.description} />
        </div>
      )}

      <div className="rounded-lg border bg-card p-4 space-y-2">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">タイムゾーン:</span>
            <span className="ml-2">{task.timezone}</span>
          </div>
          <div>
            <span className="text-muted-foreground">想定時間:</span>
            <span className="ml-2">{task.estimatedMinutes}分</span>
          </div>
          {task.tags.length > 0 && (
            <div className="col-span-2">
              <span className="text-muted-foreground">タグ:</span>
              <span className="ml-2">{task.tags.join(", ")}</span>
            </div>
          )}
        </div>
      </div>

      {task.steps && task.steps.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">ステップ ({task.steps.length})</h2>
          {task.steps.map((step) => (
            <div key={step.id} className="rounded-lg border bg-card p-4">
              <div className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
                  {step.position}
                </span>
                <span className="font-medium text-sm">{step.title}</span>
                {step.evidenceType !== "none" && (
                  <span className="text-xs text-muted-foreground">
                    [{step.evidenceType}]
                  </span>
                )}
              </div>
              {step.instruction && (
                <div className="mt-2 pl-8">
                  <MarkdownRenderer content={step.instruction} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={showDelete}
        title="タスクを削除しますか？"
        description={`「${task.title}」を削除します。この操作は取り消せません。`}
        confirmLabel="削除"
        onConfirm={handleDelete}
        onCancel={() => setShowDelete(false)}
        destructive
      />
    </div>
  );
}
