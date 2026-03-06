import { cn } from "@/lib/utils";

type Status = "in_progress" | "completed" | "abandoned" | "pending" | "skipped";

const statusConfig: Record<Status, { label: string; className: string }> = {
  pending: { label: "未着手", className: "bg-muted text-muted-foreground" },
  in_progress: { label: "実行中", className: "bg-blue-100 text-blue-700" },
  completed: { label: "完了", className: "bg-green-100 text-green-700" },
  abandoned: { label: "中断", className: "bg-red-100 text-red-700" },
  skipped: { label: "スキップ", className: "bg-yellow-100 text-yellow-700" },
};

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] ?? { label: status, className: "bg-muted" };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className,
      )}
    >
      {config.label}
    </span>
  );
}
