import { Link } from "react-router-dom";
import { AlertTriangle } from "lucide-react";
import { formatDate } from "@/lib/utils";
import type { DashboardTask } from "../types";

interface OverduePanelProps {
  tasks: DashboardTask[];
  onStartExecution: (taskId: string) => void;
}

export function OverduePanel({ tasks, onStartExecution }: OverduePanelProps) {
  if (tasks.length === 0) return null;

  return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/5">
      <div className="flex items-center gap-2 border-b border-destructive/20 px-4 py-3">
        <AlertTriangle className="h-4 w-4 text-destructive" />
        <h2 className="font-medium text-destructive">期限超過</h2>
        <span className="rounded-full bg-destructive px-2 py-0.5 text-xs text-destructive-foreground">
          {tasks.length}
        </span>
      </div>
      <div className="divide-y divide-destructive/10">
        {tasks.map((task) => (
          <div key={task.taskId} className="flex items-center justify-between px-4 py-3">
            <div>
              <Link
                to={`/tasks/${task.taskId}`}
                className="text-sm font-medium hover:underline"
              >
                {task.title}
              </Link>
              <p className="mt-0.5 text-xs text-destructive">
                {formatDate(task.scheduledFor)}
              </p>
            </div>
            <button
              onClick={() => onStartExecution(task.taskId)}
              className="rounded-md border border-destructive px-2.5 py-1 text-xs font-medium text-destructive hover:bg-destructive/10"
            >
              今すぐ実行
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
