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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <WizardProgress steps={execution.steps} currentIndex={currentIndex} />
        <div className="flex items-center gap-3">
          <StatusBadge status={execution.status} />
          {execution.status === "in_progress" && (
            <button
              onClick={() => setShowAbandon(true)}
              className="text-sm text-muted-foreground hover:text-destructive"
            >
              中断
            </button>
          )}
        </div>
      </div>

      {execution.status === "in_progress" && pendingIndex !== -1 && (
        <StepPanel
          step={execution.steps[pendingIndex]}
          onComplete={(req) => onCompleteStep(execution.steps[pendingIndex].id, req)}
          onSkip={() => onSkipStep(execution.steps[pendingIndex].id)}
        />
      )}

      {execution.status === "in_progress" && allDone && (
        <div className="rounded-lg border bg-card p-6 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            全ステップが完了しました。実行を完了してください。
          </p>
          <button
            onClick={() => onComplete()}
            className="rounded-md bg-green-600 px-6 py-2 text-sm font-medium text-white hover:bg-green-700"
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
