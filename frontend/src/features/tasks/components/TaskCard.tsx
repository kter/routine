import { Link } from "react-router-dom";
import { Clock, Tag } from "lucide-react";
import { formatCron } from "@/lib/utils";
import type { Task } from "../types";

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  return (
    <Link
      to={`/tasks/${task.id}`}
      className="block rounded-md transition-all duration-150 group"
      style={{
        background: "hsl(220 40% 8%)",
        border: "1px solid hsl(218 28% 16%)",
        borderLeft: `3px solid ${task.isActive ? "hsl(160 60% 45%)" : "hsl(218 28% 22%)"}`,
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLAnchorElement).style.borderColor = task.isActive ? "hsl(160 60% 35%)" : "hsl(218 28% 24%)";
        (e.currentTarget as HTMLAnchorElement).style.background = "hsl(220 40% 10%)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLAnchorElement).style.borderColor = "hsl(218 28% 16%)";
        (e.currentTarget as HTMLAnchorElement).style.background = "hsl(220 40% 8%)";
      }}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-sm font-medium leading-snug" style={{ color: "hsl(210 20% 88%)" }}>
            {task.title}
          </h3>
          <span
            className="shrink-0 font-mono-data text-[10px] rounded px-1.5 py-0.5 uppercase tracking-wide"
            style={
              task.isActive
                ? { color: "hsl(160 60% 55%)", background: "hsl(160 40% 8%)", border: "1px solid hsl(160 40% 15%)" }
                : { color: "hsl(215 16% 40%)", background: "hsl(218 28% 12%)", border: "1px solid hsl(218 28% 18%)" }
            }
          >
            {task.isActive ? "Active" : "Off"}
          </span>
        </div>

        {task.description && (
          <p className="mt-1.5 text-xs leading-relaxed line-clamp-2" style={{ color: "hsl(215 16% 44%)" }}>
            {task.description}
          </p>
        )}

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1 font-mono-data text-[11px]" style={{ color: "hsl(215 16% 38%)" }}>
            <Clock className="h-3 w-3" />
            {formatCron(task.cronExpression)}
          </span>
          <span className="font-mono-data text-[11px]" style={{ color: "hsl(215 16% 36%)" }}>
            {task.estimatedMinutes}分
          </span>
          {task.tags.length > 0 && (
            <span className="flex items-center gap-1 font-mono-data text-[11px]" style={{ color: "hsl(215 16% 36%)" }}>
              <Tag className="h-3 w-3" />
              {task.tags.join(", ")}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
