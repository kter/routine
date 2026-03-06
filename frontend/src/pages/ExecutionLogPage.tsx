import { useParams, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle, XCircle, SkipForward } from "lucide-react";
import { useExecution } from "@/features/executions/hooks/useExecution";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/utils";

export default function ExecutionLogPage() {
  const { id } = useParams<{ id: string }>();
  const { execution, isLoading, error } = useExecution(id!);

  if (isLoading) return <div className="text-sm text-muted-foreground">読み込み中...</div>;
  if (error || !execution) return <div className="text-sm text-destructive">実行ログが見つかりません</div>;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h1 className="text-xl font-semibold">実行ログ</h1>
      </div>

      <div className="rounded-lg border bg-card p-4 space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="font-medium">{execution.taskTitle}</span>
          <StatusBadge status={execution.status} />
        </div>
        <div className="text-muted-foreground">
          <span>開始: {formatDate(execution.startedAt)}</span>
          {execution.completedAt && (
            <span className="ml-4">完了: {formatDate(execution.completedAt)}</span>
          )}
          {execution.durationSeconds && (
            <span className="ml-4">{Math.ceil(execution.durationSeconds / 60)}分</span>
          )}
        </div>
        {execution.notes && <p className="text-muted-foreground">{execution.notes}</p>}
      </div>

      <div className="space-y-2">
        <h2 className="font-medium">ステップログ</h2>
        {execution.steps.map((step) => (
          <div key={step.id} className="rounded-lg border bg-card p-4">
            <div className="flex items-center gap-2">
              {step.status === "completed" ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : step.status === "skipped" ? (
                <SkipForward className="h-4 w-4 text-yellow-500" />
              ) : (
                <XCircle className="h-4 w-4 text-muted-foreground" />
              )}
              <span className="font-medium text-sm">{step.stepSnapshot.title}</span>
            </div>
            {step.evidenceText && (
              <div className="mt-2 pl-6">
                <p className="text-xs text-muted-foreground mb-1">証跡テキスト:</p>
                <p className="text-sm whitespace-pre-wrap">{step.evidenceText}</p>
              </div>
            )}
            {step.completedAt && (
              <p className="mt-1 pl-6 text-xs text-muted-foreground">
                {formatDate(step.completedAt)} by {step.completedBy}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
