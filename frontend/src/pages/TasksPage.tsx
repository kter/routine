import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { TaskList } from "@/features/tasks/components/TaskList";
import { useTasks } from "@/features/tasks/hooks/useTasks";

export default function TasksPage() {
  const { tasks, isLoading, error, refetch } = useTasks();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">タスク管理</h1>
        <Link
          to="/tasks/new"
          className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          新規作成
        </Link>
      </div>

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <p className="text-sm text-muted-foreground">読み込み中...</p>
        </div>
      ) : error ? (
        <div className="flex h-32 flex-col items-center justify-center gap-2">
          <p className="text-sm text-destructive">データの取得に失敗しました</p>
          <button onClick={refetch} className="text-sm text-primary hover:underline">
            再試行
          </button>
        </div>
      ) : (
        <TaskList tasks={tasks} emptyMessage="タスクが登録されていません。新規作成してください。" />
      )}
    </div>
  );
}
