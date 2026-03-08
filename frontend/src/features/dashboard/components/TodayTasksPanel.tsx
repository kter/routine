import { Link } from "react-router-dom";
import { Play, Clock } from "lucide-react";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/utils";
import type { DashboardTask } from "../types";

interface TodayTasksPanelProps {
  tasks: DashboardTask[];
  onStartExecution: (taskId: string) => void;
}

export function TodayTasksPanel({ tasks, onStartExecution }: TodayTasksPanelProps) {
  return (
    <div
      className="rounded-md flex-1 animate-fade-up"
      style={{
        background: "hsl(220 40% 8%)",
        border: "1px solid hsl(218 28% 16%)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: "1px solid hsl(218 28% 14%)" }}
      >
        <span className="font-brand text-sm font-700 tracking-tight" style={{ color: "hsl(210 20% 88%)", fontWeight: 700 }}>
          本日のタスク
        </span>
        <span
          className="font-mono-data text-[10px] rounded px-1.5 py-0.5"
          style={{
            color: tasks.length > 0 ? "hsl(43 96% 60%)" : "hsl(215 16% 44%)",
            background: tasks.length > 0 ? "hsl(43 60% 10%)" : "hsl(218 28% 14%)",
            border: `1px solid ${tasks.length > 0 ? "hsl(43 60% 18%)" : "hsl(218 28% 20%)"}`,
          }}
        >
          {tasks.length}
        </span>
      </div>

      {/* Task rows */}
      <div className="divide-y" style={{ borderColor: "hsl(218 28% 12%)" }}>
        {tasks.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <p className="text-sm" style={{ color: "hsl(215 16% 38%)" }}>
              本日のタスクはありません
            </p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.taskId}
              className="flex items-center justify-between gap-3 px-4 py-3 transition-colors duration-150"
              style={{ borderColor: "hsl(218 28% 12%)" }}
            >
              <div className="min-w-0 flex-1">
                <Link
                  to={`/tasks/${task.taskId}`}
                  className="block text-sm font-medium leading-tight hover:underline underline-offset-2 truncate"
                  style={{ color: "hsl(210 20% 85%)" }}
                >
                  {task.title}
                </Link>
                <div className="mt-1 flex items-center gap-3">
                  <span
                    className="font-mono-data text-[11px] flex items-center gap-1"
                    style={{ color: "hsl(215 16% 42%)" }}
                  >
                    <Clock className="h-3 w-3" />
                    {formatDate(task.scheduledFor)}
                  </span>
                  <span
                    className="font-mono-data text-[11px]"
                    style={{ color: "hsl(215 16% 38%)" }}
                  >
                    {task.estimatedMinutes}分
                  </span>
                </div>
              </div>

              <div className="shrink-0">
                {task.status ? (
                  <StatusBadge status={task.status} />
                ) : (
                  <button
                    onClick={() => onStartExecution(task.taskId)}
                    className="flex items-center gap-1.5 rounded px-2.5 py-1.5 text-xs font-medium transition-all duration-150"
                    style={{
                      color: "hsl(222 47% 5%)",
                      background: "hsl(43 96% 56%)",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "hsl(43 96% 64%)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background = "hsl(43 96% 56%)";
                    }}
                  >
                    <Play className="h-3 w-3 fill-current" />
                    開始
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
