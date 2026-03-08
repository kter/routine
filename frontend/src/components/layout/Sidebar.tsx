import { NavLink } from "react-router-dom";
import { LayoutDashboard, ListChecks, ClipboardList } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "ダッシュボード", end: true },
  { to: "/tasks", icon: ListChecks, label: "タスク管理" },
  { to: "/executions", icon: ClipboardList, label: "実行ログ" },
];

export function Sidebar() {
  return (
    <aside
      className="flex w-56 flex-col"
      style={{ background: "hsl(222 50% 4%)", borderRight: "1px solid hsl(218 28% 12%)" }}
    >
      {/* Brand mark */}
      <div className="flex h-14 items-center gap-3 px-4" style={{ borderBottom: "1px solid hsl(218 28% 12%)" }}>
        {/* Amber geometric mark */}
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center"
          style={{
            background: "hsl(43 96% 56%)",
            clipPath: "polygon(0 0, 100% 0, 100% 70%, 70% 100%, 0 100%)",
          }}
        >
          <span
            className="font-brand text-xs font-800 leading-none"
            style={{ color: "hsl(222 47% 5%)", fontWeight: 800 }}
          >
            R
          </span>
        </div>
        <span className="font-brand text-sm font-700 tracking-tight" style={{ color: "hsl(210 20% 88%)", fontWeight: 700 }}>
          RoutineOps
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-0.5">
        <p className="px-3 mb-2 mt-1 font-mono-data text-[10px] tracking-[0.15em] uppercase" style={{ color: "hsl(215 16% 35%)" }}>
          Navigation
        </p>
        {navItems.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-all duration-150",
                isActive
                  ? "text-[hsl(43_96%_56%)]"
                  : "text-[hsl(215_16%_50%)] hover:text-[hsl(210_20%_80%)]",
              )
            }
          >
            {({ isActive }) => (
              <>
                {/* Active left strip */}
                {isActive && (
                  <span
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full"
                    style={{ background: "hsl(43 96% 56%)" }}
                  />
                )}
                {/* Hover / active background */}
                <span
                  className={cn(
                    "absolute inset-0 rounded-md transition-opacity duration-150",
                    isActive ? "opacity-100" : "opacity-0 group-hover:opacity-100",
                  )}
                  style={{ background: isActive ? "hsl(218 30% 14%)" : "hsl(218 30% 12%)" }}
                />
                <Icon className="relative h-4 w-4 shrink-0" />
                <span className="relative">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer status strip */}
      <div
        className="px-4 py-3"
        style={{ borderTop: "1px solid hsl(218 28% 12%)" }}
      >
        <div className="flex items-center gap-2">
          <span
            className="animate-pulse-dot h-1.5 w-1.5 rounded-full"
            style={{ background: "hsl(160 60% 45%)" }}
          />
          <span className="font-mono-data text-[10px]" style={{ color: "hsl(215 16% 38%)" }}>
            SYSTEM ONLINE
          </span>
        </div>
      </div>
    </aside>
  );
}
