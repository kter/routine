import { Link } from "react-router-dom";
import { AlertTriangle, Zap } from "lucide-react";
import type { DashboardTask } from "../types";
import { toDashboardTaskViewModel } from "../view-models";

interface OverduePanelProps {
  tasks: DashboardTask[];
  onStartExecution: (taskId: string) => void;
}

export function OverduePanel({ tasks, onStartExecution }: OverduePanelProps) {
  if (tasks.length === 0) return null;

  return (
    <div
      className="rounded-md animate-fade-up"
      style={{
        background: "hsl(0 30% 8%)",
        border: "1px solid hsl(0 50% 20%)",
        borderLeft: "3px solid hsl(0 72% 54%)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: "1px solid hsl(0 40% 14%)" }}
      >
        <div className="flex items-center gap-2">
          <AlertTriangle
            className="h-3.5 w-3.5 animate-pulse-dot"
            style={{ color: "hsl(0 72% 60%)" }}
          />
          <span
            className="font-brand text-sm font-700 tracking-tight"
            style={{ color: "hsl(0 72% 65%)", fontWeight: 700 }}
          >
            期限超過
          </span>
          <span
            className="font-mono-data text-[10px] rounded px-1.5 py-0.5"
            style={{
              color: "hsl(0 72% 64%)",
              background: "hsl(0 40% 12%)",
              border: "1px solid hsl(0 40% 18%)",
            }}
          >
            {tasks.length}
          </span>
        </div>
        <span
          className="font-mono-data text-[10px]"
          style={{ color: "hsl(0 40% 40%)" }}
        >
          OVERDUE
        </span>
      </div>

      {/* Task rows */}
      <div>
        {tasks.map((task, i) => {
          const display = toDashboardTaskViewModel(task);

          return (
            <div
              key={display.taskId}
              className="flex items-center justify-between px-4 py-3 transition-colors duration-150"
              style={{
                borderTop: i > 0 ? "1px solid hsl(0 30% 12%)" : undefined,
              }}
            >
              <div className="min-w-0 flex-1">
                <Link
                  to={display.taskHref}
                  className="block text-sm font-medium leading-tight hover:underline underline-offset-2 truncate"
                  style={{ color: "hsl(210 20% 82%)" }}
                >
                  {display.title}
                </Link>
                <p
                  className="mt-0.5 font-mono-data text-[11px]"
                  style={{ color: "hsl(0 50% 48%)" }}
                >
                  {display.scheduledLabel}
                </p>
              </div>
              <button
                onClick={() => onStartExecution(display.taskId)}
                className="ml-4 flex shrink-0 items-center gap-1.5 rounded px-2.5 py-1 text-xs font-medium transition-all duration-150"
                style={{
                  color: "hsl(0 72% 65%)",
                  border: "1px solid hsl(0 50% 25%)",
                  background: "hsl(0 30% 10%)",
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLButtonElement;
                  el.style.background = "hsl(0 60% 18%)";
                  el.style.borderColor = "hsl(0 50% 35%)";
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLButtonElement;
                  el.style.background = "hsl(0 30% 10%)";
                  el.style.borderColor = "hsl(0 50% 25%)";
                }}
              >
                <Zap className="h-3 w-3" />
                今すぐ実行
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
