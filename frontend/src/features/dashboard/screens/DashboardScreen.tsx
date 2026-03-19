import { TodayTasksPanel } from "@/features/dashboard/components/TodayTasksPanel";
import { OverduePanel } from "@/features/dashboard/components/OverduePanel";
import { UpcomingPanel } from "@/features/dashboard/components/UpcomingPanel";
import { useDashboardScreen } from "@/features/dashboard/hooks/useDashboardScreen";

export function DashboardScreen() {
  const screen = useDashboardScreen();

  if (screen.status === "loading") {
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

  if (screen.status === "error") {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3">
        <p
          className="font-mono-data text-sm"
          style={{ color: "hsl(0 72% 54%)" }}
        >
          ERR: データの取得に失敗しました
        </p>
        <button
          onClick={screen.retry}
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
          {screen.dateLabel}
        </span>
      </div>

      <OverduePanel
        tasks={screen.data.overdue}
        onStartExecution={screen.handleStartExecution}
      />

      <div className="flex gap-4">
        <TodayTasksPanel
          tasks={screen.data.today}
          onStartExecution={screen.handleStartExecution}
        />
        <UpcomingPanel tasks={screen.data.upcoming} />
      </div>
    </div>
  );
}
