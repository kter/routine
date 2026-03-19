import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { PageSkeleton } from "@/components/common/PageSkeleton";
import { PageStateMessage } from "@/components/common/PageStateMessage";
import { ExecutionWizard } from "@/features/executions/components/ExecutionWizard";
import { useExecutionScreen } from "@/features/executions/hooks/useExecutionScreen";

export function ExecutionScreen() {
  const screen = useExecutionScreen();

  if (screen.status === "loading") {
    return (
      <PageSkeleton
        blocks={[
          { className: "h-5 w-48 rounded shimmer" },
          { className: "h-12 rounded-md shimmer" },
          { className: "h-64 rounded-md shimmer" },
        ]}
        className="mx-auto max-w-2xl space-y-4 animate-fade-up"
      />
    );
  }

  if (screen.status === "not_found") {
    return (
      <PageStateMessage
        title="ERR: 実行データが見つかりません"
        titleStyle={{ color: "hsl(0 72% 54%)" }}
      />
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="flex items-center justify-center rounded p-1 transition-colors duration-150"
          style={{ color: "hsl(215 16% 40%)" }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              "hsl(210 20% 75%)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              "hsl(215 16% 40%)";
          }}
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h1
          className="font-brand text-lg font-700 tracking-tight"
          style={{ fontWeight: 700 }}
        >
          {screen.title}
        </h1>
      </div>
      <ExecutionWizard
        execution={screen.execution}
        onCompleteStep={screen.completeStep}
        onSkipStep={screen.skipStep}
        onComplete={screen.completeExecution}
        onAbandon={screen.abandonExecution}
      />
    </div>
  );
}
