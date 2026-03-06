import { useAuth } from "@/features/auth/hooks/useAuth";
import { LogOut, User } from "lucide-react";

export function TopBar() {
  const { user, signOut } = useAuth();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <div />
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <User className="h-4 w-4" />
          {user?.email ?? ""}
        </span>
        <button
          onClick={signOut}
          className="flex items-center gap-1.5 rounded-md px-2 py-1 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <LogOut className="h-4 w-4" />
          ログアウト
        </button>
      </div>
    </header>
  );
}
