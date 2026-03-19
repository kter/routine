import { Link } from "react-router-dom";
import { ArrowLeft, CheckCircle2, MinusCircle, Circle } from "lucide-react";
import { PageSkeleton } from "@/components/common/PageSkeleton";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useExecutionLogScreen } from "@/features/executions/hooks/useExecutionLogScreen";
export function ExecutionLogScreen() {
  const screen = useExecutionLogScreen();

  if (screen.status === "loading") {
    return (
      <PageSkeleton
        blocks={[
          { className: "h-5 w-32 rounded shimmer" },
          { className: "h-20 rounded-md shimmer" },
          { className: "h-16 rounded-md shimmer" },
          { className: "h-16 rounded-md shimmer" },
          { className: "h-16 rounded-md shimmer" },
        ]}
        className="mx-auto max-w-2xl space-y-4 animate-fade-up"
      />
    );
  }

  if (screen.status === "not_found") {
    return (
      <PageStateMessage
        title="ERR: 実行ログが見つかりません"
        titleStyle={{ color: "hsl(0 72% 54%)" }}
      />
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-5 animate-fade-up">
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
          {screen.viewModel.title}
        </h1>
      </div>

      <div
        className="rounded-md p-4 space-y-3"
        style={{
          background: "hsl(220 40% 8%)",
          border: "1px solid hsl(218 28% 16%)",
          borderLeft: screen.viewModel.statusBorderColor,
        }}
      >
        <div className="flex items-start justify-between gap-3">
          <p className="font-medium" style={{ color: "hsl(210 20% 88%)" }}>
            {screen.viewModel.title}
          </p>
          <StatusBadge status={screen.viewModel.status} />
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-1">
          <span
            className="font-mono-data text-[11px]"
            style={{ color: "hsl(215 16% 40%)" }}
          >
            {screen.viewModel.startedLabel}
          </span>
          {screen.viewModel.completedLabel && (
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 40%)" }}
            >
              {screen.viewModel.completedLabel}
            </span>
          )}
          {screen.viewModel.durationLabel && (
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 36%)" }}
            >
              {screen.viewModel.durationLabel}
            </span>
          )}
        </div>

        {screen.viewModel.notes && (
          <p
            className="text-sm leading-relaxed"
            style={{ color: "hsl(215 16% 48%)" }}
          >
            {screen.viewModel.notes}
          </p>
        )}
      </div>

      <div>
        <h2
          className="mb-3 font-mono-data text-[11px] tracking-widest uppercase"
          style={{ color: "hsl(215 16% 36%)" }}
        >
          {screen.viewModel.stepHeading}
        </h2>

        <div className="space-y-1.5">
          {screen.viewModel.steps.map((step, i) => {
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
                        {step.title}
                      </p>
                      {step.skippedLabel && (
                        <span
                          className="shrink-0 font-mono-data text-[10px] rounded px-1.5 py-0.5 uppercase"
                          style={{
                            color: "hsl(32 95% 60%)",
                            background: "hsl(32 60% 9%)",
                            border: "1px solid hsl(32 60% 16%)",
                          }}
                        >
                          {step.skippedLabel}
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

                    {step.completedLabel && (
                      <p
                        className="mt-1.5 font-mono-data text-[10px]"
                        style={{ color: "hsl(215 16% 32%)" }}
                      >
                        {step.completedLabel}
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
