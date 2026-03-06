import { Link } from "react-router-dom";
import { Play } from "lucide-react";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/utils";
import type { DashboardTask } from "../types";

interface TodayTasksPanelProps {
  tasks: DashboardTask[];
  onStartExecution: (taskId: string) => void;
}

export function TodayTasksPanel({ tasks, onStartExecution }: TodayTasksPanelProps) {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <h2 className="font-medium">本日のタスク</h2>
        <span className="rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
          {tasks.length}
        </span>
      </div>
      <div className="divide-y">
        {tasks.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-muted-foreground">
            本日のタスクはありません
          </p>
        ) : (
          tasks.map((task) => (
            <div key={task.taskId} className="flex items-center justify-between px-4 py-3">
              <div>
                <Link
                  to={`/tasks/${task.taskId}`}
                  className="text-sm font-medium hover:underline"
                >
                  {task.title}
                </Link>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {formatDate(task.scheduledFor)} · {task.estimatedMinutes}分
                </p>
              </div>
              <div className="flex items-center gap-2">
                {task.status ? (
                  <StatusBadge status={task.status} />
                ) : (
                  <button
                    onClick={() => onStartExecution(task.taskId)}
                    className="flex items-center gap-1 rounded-md bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
                  >
                    <Play className="h-3 w-3" />
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
