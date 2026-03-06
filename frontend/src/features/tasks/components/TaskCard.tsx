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
      className="block rounded-lg border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium leading-tight">{task.title}</h3>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs ${
            task.isActive
              ? "bg-green-100 text-green-700"
              : "bg-muted text-muted-foreground"
          }`}
        >
          {task.isActive ? "有効" : "無効"}
        </span>
      </div>
      {task.description && (
        <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
          {task.description}
        </p>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock className="h-3.5 w-3.5" />
          {formatCron(task.cronExpression)}
        </span>
        <span>{task.estimatedMinutes}分</span>
        {task.tags.length > 0 && (
          <span className="flex items-center gap-1">
            <Tag className="h-3.5 w-3.5" />
            {task.tags.join(", ")}
          </span>
        )}
      </div>
    </Link>
  );
}
