import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useExecution } from "@/features/executions/hooks/useExecution";
import { ExecutionWizard } from "@/features/executions/components/ExecutionWizard";

export default function ExecutionPage() {
  const { id } = useParams<{ id: string }>();
  const {
    execution,
    isLoading,
    error,
    completeStep,
    skipStep,
    completeExecution,
    abandonExecution,
  } = useExecution(id!);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-sm text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (error || !execution) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-sm text-destructive">実行データが見つかりません</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h1 className="text-xl font-semibold">
          {execution.taskTitle ?? "タスク実行"}
        </h1>
      </div>
      <ExecutionWizard
        execution={execution}
        onCompleteStep={completeStep}
        onSkipStep={skipStep}
        onComplete={completeExecution}
        onAbandon={abandonExecution}
      />
    </div>
  );
}
