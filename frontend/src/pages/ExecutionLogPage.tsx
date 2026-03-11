import { useParams, Link } from "react-router-dom";
import { ArrowLeft, CheckCircle2, MinusCircle, Circle } from "lucide-react";
import { useExecution } from "@/features/executions/hooks/useExecution";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/utils";

export default function ExecutionLogPage() {
  const { id } = useParams<{ id: string }>();
  const { execution, isLoading, error } = useExecution(id!);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 animate-fade-up">
        <div className="h-5 w-32 rounded shimmer" />
        <div className="h-20 rounded-md shimmer" />
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 rounded-md shimmer" />
          ))}
        </div>
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
          ERR: 実行ログが見つかりません
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-5 animate-fade-up">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link
          to="/executions"
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
          実行ログ
        </h1>
      </div>

      {/* Summary card */}
      <div
        className="rounded-md p-4 space-y-3"
        style={{
          background: "hsl(220 40% 8%)",
          border: "1px solid hsl(218 28% 16%)",
          borderLeft:
            execution.status === "completed"
              ? "3px solid hsl(160 60% 45%)"
              : execution.status === "abandoned"
                ? "3px solid hsl(0 72% 54%)"
                : "3px solid hsl(43 96% 56%)",
        }}
      >
        <div className="flex items-start justify-between gap-3">
          <p className="font-medium" style={{ color: "hsl(210 20% 88%)" }}>
            {execution.taskTitle}
          </p>
          <StatusBadge status={execution.status} />
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-1">
          <span
            className="font-mono-data text-[11px]"
            style={{ color: "hsl(215 16% 40%)" }}
          >
            開始: {formatDate(execution.startedAt)}
          </span>
          {execution.completedAt && (
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 40%)" }}
            >
              完了: {formatDate(execution.completedAt)}
            </span>
          )}
          {execution.durationSeconds != null && (
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 36%)" }}
            >
              {Math.ceil(execution.durationSeconds / 60)}分
            </span>
          )}
        </div>

        {execution.notes && (
          <p
            className="text-sm leading-relaxed"
            style={{ color: "hsl(215 16% 48%)" }}
          >
            {execution.notes}
          </p>
        )}
      </div>

      {/* Step log timeline */}
      <div>
        <h2
          className="mb-3 font-mono-data text-[11px] tracking-widest uppercase"
          style={{ color: "hsl(215 16% 36%)" }}
        >
          Step Log — {execution.steps.length} steps
        </h2>

        <div className="space-y-1.5">
          {execution.steps.map((step, i) => {
            const isCompleted = step.status === "completed";
            const isSkipped = step.status === "skipped";

            return (
              <div
                key={step.id}
                className="rounded-md p-4 animate-fade-up"
                style={{
                  background: "hsl(220 40% 8%)",
                  border: "1px solid hsl(218 28% 15%)",
                  animationDelay: `${i * 0.05}s`,
                }}
              >
                <div className="flex items-start gap-3">
                  {/* Step icon */}
                  <div className="mt-0.5 shrink-0">
                    {isCompleted ? (
                      <CheckCircle2
                        className="h-4 w-4"
                        style={{ color: "hsl(160 60% 45%)" }}
                      />
                    ) : isSkipped ? (
                      <MinusCircle
                        className="h-4 w-4"
                        style={{ color: "hsl(32 95% 50%)" }}
                      />
                    ) : (
                      <Circle
                        className="h-4 w-4"
                        style={{ color: "hsl(215 16% 30%)" }}
                      />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <p
                        className="text-sm font-medium leading-snug"
                        style={{
                          color: isCompleted
                            ? "hsl(210 20% 82%)"
                            : "hsl(215 16% 50%)",
                        }}
                      >
                        {step.stepSnapshot.title}
                      </p>
                      {isSkipped && (
                        <span
                          className="shrink-0 font-mono-data text-[10px] rounded px-1.5 py-0.5 uppercase"
                          style={{
                            color: "hsl(32 95% 60%)",
                            background: "hsl(32 60% 9%)",
                            border: "1px solid hsl(32 60% 16%)",
                          }}
                        >
                          Skip
                        </span>
                      )}
                    </div>

                    {step.evidenceText && (
                      <div className="mt-2">
                        <p
                          className="font-mono-data text-[10px] uppercase tracking-widest mb-1"
                          style={{ color: "hsl(215 16% 34%)" }}
                        >
                          Evidence
                        </p>
                        <p
                          className="text-xs whitespace-pre-wrap leading-relaxed"
                          style={{ color: "hsl(215 16% 52%)" }}
                        >
                          {step.evidenceText}
                        </p>
                      </div>
                    )}

                    {step.completedAt && (
                      <p
                        className="mt-1.5 font-mono-data text-[10px]"
                        style={{ color: "hsl(215 16% 32%)" }}
                      >
                        {formatDate(step.completedAt)} · {step.completedBy}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
