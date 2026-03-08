import { cn } from "@/lib/utils";

type Status = "in_progress" | "completed" | "abandoned" | "pending" | "skipped";

const statusConfig: Record<Status, { label: string; dot: string; style: React.CSSProperties }> = {
  pending: {
    label: "未着手",
    dot: "hsl(215 16% 44%)",
    style: { color: "hsl(215 16% 55%)", background: "hsl(218 28% 14%)", border: "1px solid hsl(218 28% 20%)" },
  },
  in_progress: {
    label: "実行中",
    dot: "hsl(43 96% 56%)",
    style: { color: "hsl(43 96% 65%)", background: "hsl(43 60% 10%)", border: "1px solid hsl(43 60% 18%)" },
  },
  completed: {
    label: "完了",
    dot: "hsl(160 60% 45%)",
    style: { color: "hsl(160 60% 55%)", background: "hsl(160 40% 8%)", border: "1px solid hsl(160 40% 15%)" },
  },
  abandoned: {
    label: "中断",
    dot: "hsl(0 72% 54%)",
    style: { color: "hsl(0 72% 64%)", background: "hsl(0 40% 10%)", border: "1px solid hsl(0 40% 18%)" },
  },
  skipped: {
    label: "スキップ",
    dot: "hsl(32 95% 50%)",
    style: { color: "hsl(32 95% 60%)", background: "hsl(32 60% 9%)", border: "1px solid hsl(32 60% 16%)" },
  },
};

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] ?? {
    label: status,
    dot: "hsl(215 16% 44%)",
    style: { color: "hsl(215 16% 55%)", background: "hsl(218 28% 14%)", border: "1px solid hsl(218 28% 20%)" },
  };

  const isPulsing = status === "in_progress";

  return (
    <span
      className={cn("inline-flex items-center gap-1.5 rounded px-2 py-0.5 font-mono-data text-[10px] tracking-wide uppercase", className)}
      style={config.style}
    >
      <span
        className={cn("h-1.5 w-1.5 rounded-full shrink-0", isPulsing && "animate-pulse-dot")}
        style={{ background: config.dot }}
      />
      {config.label}
    </span>
  );
}
