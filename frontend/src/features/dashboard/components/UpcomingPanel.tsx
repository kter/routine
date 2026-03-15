import { Link } from "react-router-dom";
import type { DashboardTask } from "../types";
import { toDashboardTaskViewModel } from "../view-models";

interface UpcomingPanelProps {
  tasks: DashboardTask[];
}

export function UpcomingPanel({ tasks }: UpcomingPanelProps) {
  return (
    <div
      className="rounded-md flex-1 animate-fade-up"
      style={{
        background: "hsl(220 40% 8%)",
        border: "1px solid hsl(218 28% 16%)",
        animationDelay: "0.05s",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: "1px solid hsl(218 28% 14%)" }}
      >
        <span
          className="font-brand text-sm font-700 tracking-tight"
          style={{ color: "hsl(210 20% 88%)", fontWeight: 700 }}
        >
          今後7日間
        </span>
        <span
          className="font-mono-data text-[10px] tracking-widest uppercase"
          style={{ color: "hsl(215 16% 34%)" }}
        >
          Upcoming
        </span>
      </div>

      {/* Task rows */}
      <div className="divide-y" style={{ borderColor: "hsl(218 28% 12%)" }}>
        {tasks.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <p className="text-sm" style={{ color: "hsl(215 16% 38%)" }}>
              予定されたタスクはありません
            </p>
          </div>
        ) : (
          tasks.map((task) => {
            const display = toDashboardTaskViewModel(task);

            return (
              <div
                key={`${display.taskId}-${display.scheduledLabel}`}
                className="flex items-center justify-between gap-4 px-4 py-2.5"
                style={{ borderColor: "hsl(218 28% 12%)" }}
              >
                <Link
                  to={display.taskHref}
                  className="min-w-0 flex-1 truncate text-sm hover:underline underline-offset-2"
                  style={{ color: "hsl(210 20% 75%)" }}
                >
                  {display.title}
                </Link>
                <span
                  className="shrink-0 font-mono-data text-[11px]"
                  style={{ color: "hsl(215 16% 40%)" }}
                >
                  {display.scheduledLabel}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
