import { PageSkeleton } from "@/components/common/PageSkeleton";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { TodayTasksPanel } from "@/features/dashboard/components/TodayTasksPanel";
import { OverduePanel } from "@/features/dashboard/components/OverduePanel";
import { UpcomingPanel } from "@/features/dashboard/components/UpcomingPanel";
import { useDashboardScreen } from "@/features/dashboard/hooks/useDashboardScreen";

export function DashboardScreen() {
  const screen = useDashboardScreen();

  if (screen.status === "loading") {
    return (
      <PageSkeleton
        blocks={[
          { className: "h-5 w-32 rounded shimmer md:col-span-2" },
          { className: "h-48 rounded-md shimmer md:col-span-2" },
          { className: "h-64 rounded-md shimmer" },
          { className: "h-64 rounded-md shimmer" },
        ]}
        className="grid animate-fade-up gap-4 md:grid-cols-2"
      />
    );
  }

  if (screen.status === "error") {
    return (
      <PageStateMessage
        title="ERR: データの取得に失敗しました"
        actionLabel="再試行 →"
        onAction={screen.retry}
        titleStyle={{ color: "hsl(0 72% 54%)" }}
        actionStyle={{ color: "hsl(43 96% 56%)" }}
      />
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
