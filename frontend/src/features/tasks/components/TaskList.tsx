import { TaskCard } from "./TaskCard";
import type { Task } from "../types";

interface TaskListProps {
  tasks: Task[];
  emptyMessage?: string;
}

export function TaskList({ tasks, emptyMessage = "タスクがありません" }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div
        className="flex h-32 flex-col items-center justify-center gap-1 rounded-md"
        style={{ border: "1px dashed hsl(218 28% 18%)" }}
      >
        <p className="font-mono-data text-[10px] tracking-widest uppercase" style={{ color: "hsl(215 16% 28%)" }}>
          No tasks
        </p>
        <p className="text-sm" style={{ color: "hsl(215 16% 38%)" }}>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
