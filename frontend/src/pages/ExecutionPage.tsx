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
      <div className="mx-auto max-w-2xl space-y-4 animate-fade-up">
        <div className="h-5 w-48 rounded shimmer" />
        <div className="h-12 rounded-md shimmer" />
        <div className="h-64 rounded-md shimmer" />
      </div>
    );
  }

  if (error || !execution) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p
          className="font-mono-data text-sm"
          style={{ color: "hsl(0 72% 54%)" }}
        >
          ERR: 実行データが見つかりません
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="flex items-center justify-center rounded p-1 transition-colors duration-150"
          style={{ color: "hsl(215 16% 40%)" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              "hsl(210 20% 75%)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              "hsl(215 16% 40%)";
          }}
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
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
