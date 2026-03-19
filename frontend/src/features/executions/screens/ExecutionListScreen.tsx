import { Link } from "react-router-dom";
import { PageSkeleton } from "@/components/common/PageSkeleton";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { useExecutionListScreen } from "@/features/executions/hooks/useExecutionListScreen";
import { toExecutionListItemViewModel } from "@/features/executions/view-models";

function ExecutionRow({
  execution,
  index,
}: {
  execution: Parameters<typeof toExecutionListItemViewModel>[0];
  index: number;
}) {
  const row = toExecutionListItemViewModel(execution);

  return (
    <Link
      to={row.href}
      className="group relative flex items-start gap-0 overflow-hidden rounded-md transition-all duration-150 animate-fade-up"
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
      <div
        className="w-0.5 shrink-0 self-stretch"
        style={{ background: row.stripColor, opacity: row.isActive ? 1 : 0.5 }}
      />

      <div className="flex flex-1 items-center gap-4 px-4 py-3">
        <div className="flex shrink-0 flex-col items-center gap-1">
          <span
            className={`h-2 w-2 rounded-full ${row.isActive ? "animate-pulse-dot" : ""}`}
            style={{ background: row.dotColor }}
          />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-3">
            <p
              className="truncate text-sm font-medium"
              style={{ color: "hsl(210 20% 86%)" }}
            >
              {row.title}
            </p>
            <span
              className="shrink-0 rounded px-2 py-0.5 font-mono-data text-[10px] uppercase tracking-wide"
              style={row.statusLabelStyle}
            >
              {row.statusLabel}
            </span>
          </div>

          <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-0.5">
            <span
              className="font-mono-data text-[11px]"
              style={{ color: "hsl(215 16% 38%)" }}
            >
              {row.startedLabel}
            </span>
            {row.stepsLabel && (
              <span
                className="font-mono-data text-[11px]"
                style={{ color: "hsl(215 16% 36%)" }}
              >
                {row.stepsLabel}
              </span>
            )}
            {row.durationLabel && (
              <span
                className="font-mono-data text-[11px]"
                style={{ color: "hsl(215 16% 34%)" }}
              >
                {row.durationLabel}
              </span>
            )}
          </div>
        </div>

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

export function ExecutionListScreen() {
  const screen = useExecutionListScreen();

  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between">
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
          実行ログ
        </h1>
        {screen.status === "ready" && (
          <span
            className="font-mono-data text-[11px]"
            style={{ color: "hsl(215 16% 34%)" }}
          >
            {screen.recordsLabel}
          </span>
        )}
      </div>

      {screen.status === "loading" ? (
        <PageSkeleton
          blocks={[0, 1, 2, 3].map((i) => ({
            className: "h-16 rounded-md shimmer",
            style: { animationDelay: `${i * 0.08}s`, opacity: 1 - i * 0.15 },
          }))}
          className="space-y-2"
        />
      ) : screen.status === "error" ? (
        <PageStateMessage
          title="ERR: データの取得に失敗しました"
          actionLabel="再試行 →"
          onAction={screen.retry}
          className="flex h-40 flex-col items-center justify-center gap-3 rounded-md"
          style={{ border: "1px solid hsl(218 28% 14%)" }}
          titleStyle={{ color: "hsl(0 72% 54%)" }}
          actionStyle={{ color: "hsl(43 96% 56%)" }}
        />
      ) : screen.executions.length === 0 ? (
        <PageStateMessage
          title="No records"
          description="実行ログがありません"
          className="flex h-40 flex-col items-center justify-center gap-2 rounded-md"
          style={{ border: "1px dashed hsl(218 28% 18%)" }}
          titleClassName="font-mono-data text-[11px] tracking-widest uppercase"
          titleStyle={{ color: "hsl(215 16% 30%)" }}
          descriptionStyle={{ color: "hsl(215 16% 36%)" }}
        />
      ) : (
        <div className="space-y-1.5">
          {screen.executions.map((execution, index) => (
            <ExecutionRow
              key={execution.id}
              execution={execution}
              index={index}
            />
          ))}
        </div>
      )}
    </div>
  );
}
