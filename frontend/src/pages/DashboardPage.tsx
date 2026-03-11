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
      <div className="space-y-4 animate-fade-up">
        <div className="h-5 w-32 rounded shimmer" />
        <div className="h-48 rounded-md shimmer" />
        <div className="flex gap-4">
          <div className="h-64 flex-1 rounded-md shimmer" />
          <div className="h-64 flex-1 rounded-md shimmer" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3">
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
    );
  }

  return (
    <div className="space-y-4">
      {/* Page heading */}
      <div className="flex items-baseline gap-3">
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
          ダッシュボード
        </h1>
        <span
          className="font-mono-data text-[11px]"
          style={{ color: "hsl(215 16% 36%)" }}
        >
          {new Date().toLocaleDateString("ja-JP", {
            year: "numeric",
            month: "long",
            day: "numeric",
            weekday: "short",
          })}
        </span>
      </div>

      {/* Overdue alert — full width */}
      <OverduePanel
        tasks={data.overdue}
        onStartExecution={handleStartExecution}
      />

      {/* Two-column grid: today + upcoming */}
      <div className="flex gap-4">
        <TodayTasksPanel
          tasks={data.today}
          onStartExecution={handleStartExecution}
        />
        <UpcomingPanel tasks={data.upcoming} />
      </div>
    </div>
  );
}
