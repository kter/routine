import { Link } from "react-router-dom";
import { Calendar } from "lucide-react";
import { formatDate } from "@/lib/utils";
import type { DashboardTask } from "../types";

interface UpcomingPanelProps {
  tasks: DashboardTask[];
}

export function UpcomingPanel({ tasks }: UpcomingPanelProps) {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center gap-2 border-b px-4 py-3">
        <Calendar className="h-4 w-4 text-muted-foreground" />
        <h2 className="font-medium">今後7日間</h2>
      </div>
      <div className="divide-y">
        {tasks.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-muted-foreground">
            予定されたタスクはありません
          </p>
        ) : (
          tasks.map((task) => (
            <div key={`${task.taskId}-${task.scheduledFor}`} className="flex items-center justify-between px-4 py-3">
              <Link
                to={`/tasks/${task.taskId}`}
                className="text-sm font-medium hover:underline"
              >
                {task.title}
              </Link>
              <span className="text-xs text-muted-foreground">
                {formatDate(task.scheduledFor)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
