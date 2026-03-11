import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { TaskList } from "@/features/tasks/components/TaskList";
import { useTasks } from "@/features/tasks/hooks/useTasks";

export default function TasksPage() {
  const { tasks, isLoading, error, refetch } = useTasks();

  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between">
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
          タスク管理
        </h1>
        <Link
          to="/tasks/new"
          className="flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-medium transition-all duration-150"
          style={{
            color: "hsl(222 47% 5%)",
            background: "hsl(43 96% 56%)",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.background =
              "hsl(43 96% 64%)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.background =
              "hsl(43 96% 56%)";
          }}
        >
          <Plus className="h-3.5 w-3.5" />
          新規作成
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-md shimmer"
              style={{ opacity: 1 - i * 0.2 }}
            />
          ))}
        </div>
      ) : error ? (
        <div
          className="flex h-40 flex-col items-center justify-center gap-3 rounded-md"
          style={{ border: "1px solid hsl(218 28% 14%)" }}
        >
          <p
            className="font-mono-data text-sm"
            style={{ color: "hsl(0 72% 54%)" }}
          >
            ERR: データの取得に失敗しました
          </p>
          <button
            onClick={refetch}
            className="font-mono-data text-xs hover:underline"
            style={{ color: "hsl(43 96% 56%)" }}
          >
            再試行 →
          </button>
        </div>
      ) : (
        <TaskList
          tasks={tasks}
          emptyMessage="タスクが登録されていません。新規作成してください。"
        />
      )}
    </div>
  );
}
