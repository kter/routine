import { useAuth } from "@/features/auth/hooks/useAuth";
import { LogOut } from "lucide-react";

export function TopBar() {
  const { user, signOut } = useAuth();

  return (
    <header
      className="flex h-14 items-center justify-end gap-4 px-6"
      style={{ borderBottom: "1px solid hsl(218 28% 14%)", background: "hsl(220 40% 7%)" }}
    >
      <span
        className="font-mono-data text-xs"
        style={{ color: "hsl(215 16% 44%)" }}
      >
        {user?.email ?? ""}
      </span>
      <div
        className="h-3.5 w-px"
        style={{ background: "hsl(218 28% 20%)" }}
      />
      <button
        onClick={signOut}
        className="flex items-center gap-1.5 rounded px-2 py-1 text-xs transition-colors duration-150"
        style={{ color: "hsl(215 16% 44%)" }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.color = "hsl(0 72% 60%)";
          (e.currentTarget as HTMLButtonElement).style.background = "hsl(0 30% 10%)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.color = "hsl(215 16% 44%)";
          (e.currentTarget as HTMLButtonElement).style.background = "transparent";
        }}
      >
        <LogOut className="h-3.5 w-3.5" />
        ログアウト
      </button>
    </header>
  );
}
