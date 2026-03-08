import { useState } from "react";
import { WizardProgress } from "./WizardProgress";
import { StepPanel } from "./StepPanel";
import { StatusBadge } from "@/components/common/StatusBadge";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import type { Execution } from "../types";

interface ExecutionWizardProps {
  execution: Execution;
  onCompleteStep: ReturnType<typeof import("../hooks/useExecution").useExecution>["completeStep"];
  onSkipStep: ReturnType<typeof import("../hooks/useExecution").useExecution>["skipStep"];
  onComplete: ReturnType<typeof import("../hooks/useExecution").useExecution>["completeExecution"];
  onAbandon: ReturnType<typeof import("../hooks/useExecution").useExecution>["abandonExecution"];
}

export function ExecutionWizard({
  execution,
  onCompleteStep,
  onSkipStep,
  onComplete,
  onAbandon,
}: ExecutionWizardProps) {
  const [showAbandon, setShowAbandon] = useState(false);
  const pendingIndex = execution.steps.findIndex((s) => s.status === "pending");
  const currentIndex = pendingIndex === -1 ? execution.steps.length - 1 : pendingIndex;

  const allDone = execution.steps.every((s) => s.status !== "pending");

  return (
    <div className="space-y-5">
      {/* Progress bar + status row */}
      <div
        className="flex items-center justify-between rounded-md px-4 py-3"
        style={{ background: "hsl(220 40% 8%)", border: "1px solid hsl(218 28% 16%)" }}
      >
        <WizardProgress steps={execution.steps} currentIndex={currentIndex} />
        <div className="flex items-center gap-4">
          <StatusBadge status={execution.status} />
          {execution.status === "in_progress" && (
            <button
              onClick={() => setShowAbandon(true)}
              className="font-mono-data text-[11px] transition-colors duration-150"
              style={{ color: "hsl(215 16% 38%)" }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = "hsl(0 72% 54%)"; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = "hsl(215 16% 38%)"; }}
            >
              中断
            </button>
          )}
        </div>
      </div>

      {/* Current step */}
      {execution.status === "in_progress" && pendingIndex !== -1 && (
        <StepPanel
          step={execution.steps[pendingIndex]}
          onComplete={(req) => onCompleteStep(execution.steps[pendingIndex].id, req)}
          onSkip={() => onSkipStep(execution.steps[pendingIndex].id)}
        />
      )}

      {/* All steps done — completion prompt */}
      {execution.status === "in_progress" && allDone && (
        <div
          className="rounded-md px-6 py-8 text-center animate-fade-up"
          style={{ background: "hsl(220 40% 8%)", border: "1px solid hsl(160 40% 15%)", borderLeft: "3px solid hsl(160 60% 45%)" }}
        >
          <p className="font-mono-data text-[11px] tracking-widest uppercase mb-1" style={{ color: "hsl(160 60% 45%)" }}>
            All steps complete
          </p>
          <p className="mb-5 text-sm" style={{ color: "hsl(215 16% 55%)" }}>
            全ステップが完了しました。実行を完了してください。
          </p>
          <button
            onClick={() => onComplete()}
            className="rounded px-6 py-2 text-sm font-medium transition-all duration-150"
            style={{ color: "hsl(222 47% 5%)", background: "hsl(160 60% 45%)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "hsl(160 60% 52%)"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "hsl(160 60% 45%)"; }}
          >
            実行完了
          </button>
        </div>
      )}

      <ConfirmDialog
        open={showAbandon}
        title="実行を中断しますか？"
        description="この実行を中断します。中断後は再開できません。"
        confirmLabel="中断する"
        onConfirm={() => { setShowAbandon(false); onAbandon(); }}
        onCancel={() => setShowAbandon(false)}
        destructive
      />
    </div>
  );
}
