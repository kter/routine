import { Link } from "react-router-dom";
import { Edit, Play, Trash2 } from "lucide-react";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useTaskDetailScreen } from "../hooks";
export function TaskDetailScreen() {
  const screen = useTaskDetailScreen();

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
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">{screen.viewModel.title}</h1>
          <div className="mt-1 flex items-center gap-2">
            <StatusBadge status={screen.viewModel.status} />
            <span className="text-sm text-muted-foreground">
              {screen.viewModel.scheduleLabel}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={screen.handleStartExecution}
            className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground"
          >
            <Play className="h-4 w-4" />
            実行
          </button>
          <Link
            to={screen.viewModel.editHref}
            className="flex items-center gap-1.5 rounded-md border px-3 py-2 text-sm hover:bg-accent"
          >
            <Edit className="h-4 w-4" />
            編集
          </Link>
          <button
            onClick={screen.openDeleteDialog}
            className="flex items-center gap-1.5 rounded-md border border-destructive px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {screen.task.description && (
        <div className="rounded-lg border bg-card p-4">
          <MarkdownRenderer content={screen.task.description} />
        </div>
      )}

      <div className="rounded-lg border bg-card p-4 space-y-2">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">タイムゾーン:</span>
            <span className="ml-2">{screen.viewModel.timezoneLabel}</span>
          </div>
          <div>
            <span className="text-muted-foreground">想定時間:</span>
            <span className="ml-2">
              {screen.viewModel.estimatedMinutesLabel}
            </span>
          </div>
          {screen.viewModel.tagsLabel && (
            <div className="col-span-2">
              <span className="text-muted-foreground">タグ:</span>
              <span className="ml-2">{screen.viewModel.tagsLabel}</span>
            </div>
          )}
        </div>
      </div>

      {screen.viewModel.steps.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">
            ステップ ({screen.viewModel.steps.length})
          </h2>
          {screen.viewModel.steps.map((step) => (
            <div key={step.id} className="rounded-lg border bg-card p-4">
              <div className="flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
                  {step.position}
                </span>
                <span className="font-medium text-sm">{step.title}</span>
                {step.evidenceLabel && (
                  <span className="text-xs text-muted-foreground">
                    {step.evidenceLabel}
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
        open={screen.showDelete}
        title="タスクを削除しますか？"
        description={screen.viewModel.deleteDescription}
        confirmLabel="削除"
        onConfirm={screen.handleDelete}
        onCancel={screen.closeDeleteDialog}
        destructive
      />
    </div>
  );
}
