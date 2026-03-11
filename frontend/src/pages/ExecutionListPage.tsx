import { Link } from "react-router-dom";
import { useExecutions } from "@/features/executions/hooks/useExecution";
import type { Execution } from "@/features/executions/types";

const STATUS_CONFIG: Record<
  Execution["status"],
  {
    label: string;
    dotColor: string;
    stripColor: string;
    labelStyle: React.CSSProperties;
  }
> = {
  in_progress: {
    label: "実行中",
    dotColor: "hsl(43 96% 56%)",
    stripColor: "hsl(43 96% 56%)",
    labelStyle: {
      color: "hsl(43 96% 65%)",
      background: "hsl(43 60% 10%)",
      border: "1px solid hsl(43 60% 18%)",
    },
  },
  completed: {
    label: "完了",
    dotColor: "hsl(160 60% 45%)",
    stripColor: "hsl(160 60% 45%)",
    labelStyle: {
      color: "hsl(160 60% 55%)",
      background: "hsl(160 40% 8%)",
      border: "1px solid hsl(160 40% 15%)",
    },
  },
  abandoned: {
    label: "中断",
    dotColor: "hsl(215 16% 36%)",
    stripColor: "hsl(218 28% 24%)",
    labelStyle: {
      color: "hsl(215 16% 50%)",
      background: "hsl(218 28% 12%)",
      border: "1px solid hsl(218 28% 18%)",
    },
  },
};

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return s > 0 ? `${m}m ${s}s` : `${m}m`;
}

function ExecutionRow({
  execution,
  index,
}: {
  execution: Execution;
  index: number;
}) {
  const cfg = STATUS_CONFIG[execution.status];
  const startedAt = new Date(execution.startedAt);
  const isActive = execution.status === "in_progress";

  const dateStr = startedAt.toLocaleDateString("ja-JP", {
    month: "numeric",
    day: "numeric",
  });
  const timeStr = startedAt.toLocaleTimeString("ja-JP", {
    hour: "2-digit",
    minute: "2-digit",
  });

  const completedSteps = execution.steps.filter(
    (s) => s.status === "completed",
  ).length;
  const totalSteps = execution.steps.length;

  return (
    <Link
      to={`/executions/${execution.id}`}
      className="group relative flex items-start gap-0 rounded-md overflow-hidden transition-all duration-150 animate-fade-up"
      style={{
        background: "hsl(220 40% 8%)",
        border: "1px solid hsl(218 28% 15%)",
        animationDelay: `${index * 0.04}s`,
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLAnchorElement).style.background =
          "hsl(220 40% 10%)";
        (e.currentTarget as HTMLAnchorElement).style.borderColor =
          "hsl(218 28% 22%)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLAnchorElement).style.background =
          "hsl(220 40% 8%)";
        (e.currentTarget as HTMLAnchorElement).style.borderColor =
          "hsl(218 28% 15%)";
      }}
    >
      {/* Status color strip — left border */}
      <div
        className="shrink-0 self-stretch w-0.5"
        style={{ background: cfg.stripColor, opacity: isActive ? 1 : 0.5 }}
      />

      <div className="flex flex-1 items-center gap-4 px-4 py-3">
        {/* Status dot */}
        <div className="shrink-0 flex flex-col items-center gap-1">
          <span
            className={`h-2 w-2 rounded-full ${isActive ? "animate-pulse-dot" : ""}`}
            style={{ background: cfg.dotColor }}
          />
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-3">
            <p
              className="text-sm font-medium truncate"
              style={{ color: "hsl(210 20% 86%)" }}
            >
              {execution.taskTitle ?? execution.taskId}
            </p>
            {/* Status badge */}
            <span
              className="shrink-0 font-mono-data text-[10px] rounded px-2 py-0.5 uppercase tracking-wide"
              style={cfg.labelStyle}
            >
              {cfg.label}
            </span>
          </div>

          {/* Metadata row */}
          <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-0.5">
            {/* Date / time */}
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 38%)" }}
            >
              {dateStr} · {timeStr}
            </span>

            {/* Step progress */}
            {totalSteps > 0 && (
              <span
                className="font-mono-data text-[11px]"
                style={{ color: "hsl(215 16% 36%)" }}
              >
                {completedSteps}/{totalSteps} steps
              </span>
            )}

            {/* Duration */}
            {execution.durationSeconds != null && (
              <span
                className="font-mono-data text-[11px]"
                style={{ color: "hsl(215 16% 34%)" }}
              >
                {formatDuration(execution.durationSeconds)}
              </span>
            )}
          </div>
        </div>

        {/* Arrow */}
        <span
          className="shrink-0 font-mono-data text-xs transition-transform duration-150 group-hover:translate-x-0.5"
          style={{ color: "hsl(215 16% 30%)" }}
        >
          →
        </span>
      </div>
    </Link>
  );
}

export default function ExecutionListPage() {
  const { executions, isLoading, error, refetch } = useExecutions();

  return (
    <div className="space-y-4">
      {/* Page heading */}
      <div className="flex items-baseline justify-between">
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
          実行ログ
        </h1>
        {!isLoading && !error && (
          <span
            className="font-mono-data text-[11px]"
            style={{ color: "hsl(215 16% 34%)" }}
          >
            {executions.length} records
          </span>
        )}
      </div>

      {/* States */}
      {isLoading ? (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-16 rounded-md shimmer"
              style={{ animationDelay: `${i * 0.08}s`, opacity: 1 - i * 0.15 }}
            />
          ))}
        </div>
      ) : error ? (
        <div
          className="flex h-40 flex-col items-center justify-center gap-3 rounded-md"
          style={{ border: "1px solid hsl(218 28% 14%)" }}
        >
          <p
            className="font-mono-data text-sm"
            style={{ color: "hsl(0 72% 54%)" }}
          >
            ERR: データの取得に失敗しました
          </p>
          <button
            onClick={refetch}
            className="font-mono-data text-xs hover:underline"
            style={{ color: "hsl(43 96% 56%)" }}
          >
            再試行 →
          </button>
        </div>
      ) : executions.length === 0 ? (
        <div
          className="flex h-40 flex-col items-center justify-center gap-2 rounded-md"
          style={{ border: "1px dashed hsl(218 28% 18%)" }}
        >
          <span
            className="font-mono-data text-[11px] tracking-widest uppercase"
            style={{ color: "hsl(215 16% 30%)" }}
          >
            No records
          </span>
          <p className="text-sm" style={{ color: "hsl(215 16% 36%)" }}>
            実行ログがありません
          </p>
        </div>
      ) : (
        <div className="space-y-1.5">
          {executions.map((execution, i) => (
            <ExecutionRow key={execution.id} execution={execution} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
