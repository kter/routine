import { Navigate } from "react-router-dom";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { useAuth } from "@/features/auth/hooks/useAuth";

export default function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;

  return (
    <div
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-dot-grid"
      style={{ background: "hsl(222 47% 4%)" }}
    >
      {/* Ambient glow */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 60%, hsl(43 96% 56% / 0.06) 0%, transparent 70%), radial-gradient(ellipse 40% 30% at 20% 30%, hsl(210 80% 56% / 0.04) 0%, transparent 70%)",
        }}
      />

      {/* Decorative corner lines */}
      <svg
        className="pointer-events-none absolute inset-0 h-full w-full opacity-20"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* top-left corner bracket */}
        <path
          d="M0 80 L0 0 L80 0"
          fill="none"
          stroke="hsl(43 96% 56%)"
          strokeWidth="1"
        />
        {/* bottom-right corner bracket */}
        <path
          d="M100% -80px L100% 100% L calc(100% - 80px) 100%"
          fill="none"
          stroke="hsl(43 96% 56%)"
          strokeWidth="1"
        />
      </svg>

      {/* Login card */}
      <div
        className="relative w-full max-w-sm animate-fade-up"
        style={{ animationDuration: "0.4s" }}
      >
        {/* Top accent line */}
        <div
          className="absolute -top-px left-8 right-8 h-px"
          style={{
            background:
              "linear-gradient(90deg, transparent, hsl(43 96% 56%), transparent)",
          }}
        />

        <div
          className="rounded-md px-8 py-9"
          style={{
            background: "hsl(220 40% 7%)",
            border: "1px solid hsl(218 28% 16%)",
          }}
        >
          {/* Brand mark */}
          <div className="mb-8 flex flex-col items-center gap-3">
            <div
              className="flex h-10 w-10 items-center justify-center"
              style={{
                background: "hsl(43 96% 56%)",
                clipPath: "polygon(0 0, 100% 0, 100% 70%, 70% 100%, 0 100%)",
              }}
            >
              <span
                className="font-brand text-base leading-none"
                style={{ color: "hsl(222 47% 5%)", fontWeight: 800 }}
              >
                R
              </span>
            </div>
            <div className="text-center">
              <h1
                className="font-brand text-xl tracking-tight"
                style={{ color: "hsl(210 20% 90%)", fontWeight: 700 }}
              >
                RoutineOps
              </h1>
              <p
                className="mt-0.5 font-mono-data text-[11px] tracking-widest uppercase"
                style={{ color: "hsl(215 16% 38%)" }}
              >
                定期作業トラッカー
              </p>
            </div>
          </div>

          {/* Divider */}
          <div
            className="mb-6 h-px"
            style={{ background: "hsl(218 28% 16%)" }}
          />

          <LoginForm />
        </div>

        {/* Bottom label */}
        <p
          className="mt-4 text-center font-mono-data text-[10px] tracking-widest uppercase"
          style={{ color: "hsl(215 16% 26%)" }}
        >
          Secure · AWS Cognito
        </p>
      </div>
    </div>
  );
}
