import { useNavigate } from "react-router-dom";
import { TodayTasksPanel } from "@/features/dashboard/components/TodayTasksPanel";
import { OverduePanel } from "@/features/dashboard/components/OverduePanel";
import { UpcomingPanel } from "@/features/dashboard/components/UpcomingPanel";
import { useDashboard } from "@/features/dashboard/hooks/useDashboard";
import { executionsApi } from "@/lib/api/executions";

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard();
  const navigate = useNavigate();

  const handleStartExecution = async (taskId: string) => {
    const execution = await executionsApi.start({ taskId });
    navigate(`/executions/${execution.id}`);
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-sm text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-2">
        <p className="text-sm text-destructive">データの取得に失敗しました</p>
        <button onClick={refetch} className="text-sm text-primary hover:underline">
          再試行
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">ダッシュボード</h1>
      <OverduePanel tasks={data.overdue} onStartExecution={handleStartExecution} />
      <TodayTasksPanel tasks={data.today} onStartExecution={handleStartExecution} />
      <UpcomingPanel tasks={data.upcoming} />
    </div>
  );
}
