import { useState } from "react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { EvidenceUpload } from "./EvidenceUpload";
import type { ExecutionStep, CompleteStepRequest } from "../types";

interface StepPanelProps {
  step: ExecutionStep;
  onComplete: (req: CompleteStepRequest) => Promise<void>;
  onSkip: () => Promise<void>;
}

export function StepPanel({ step, onComplete, onSkip }: StepPanelProps) {
  const [evidenceText, setEvidenceText] = useState("");
  const [evidenceImageKey, setEvidenceImageKey] = useState<string | undefined>();
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { title, instruction, evidenceType, isRequired } = step.stepSnapshot;

  const handleComplete = async () => {
    setIsSubmitting(true);
    try {
      await onComplete({
        evidenceText: evidenceType === "text" ? evidenceText : undefined,
        evidenceImageKey: evidenceType === "image" ? evidenceImageKey : undefined,
        notes,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const canComplete =
    step.status === "pending" &&
    (evidenceType === "none" ||
      (evidenceType === "text" && evidenceText.trim()) ||
      (evidenceType === "image" && evidenceImageKey));

  return (
    <div className="space-y-4 rounded-lg border bg-card p-6">
      <div>
        <h3 className="text-lg font-medium">{title}</h3>
        {instruction && (
          <div className="mt-3">
            <MarkdownRenderer content={instruction} />
          </div>
        )}
      </div>

      {evidenceType === "text" && step.status === "pending" && (
        <div className="space-y-1">
          <label className="block text-sm font-medium">証跡テキスト *</label>
          <textarea
            value={evidenceText}
            onChange={(e) => setEvidenceText(e.target.value)}
            rows={4}
            placeholder="実施内容や確認結果を入力してください"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      )}

      {evidenceType === "image" && step.status === "pending" && (
        <EvidenceUpload
          executionId={step.executionId}
          stepId={step.id}
          onUploaded={setEvidenceImageKey}
        />
      )}

      <div className="space-y-1">
        <label className="block text-sm font-medium">メモ（任意）</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          placeholder="補足事項があれば入力"
          className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      {step.status === "pending" && (
        <div className="flex gap-3">
          <button
            onClick={handleComplete}
            disabled={!canComplete || isSubmitting}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? "処理中..." : "完了"}
          </button>
          {!isRequired && (
            <button
              onClick={onSkip}
              disabled={isSubmitting}
              className="rounded-md border px-4 py-2 text-sm hover:bg-accent disabled:opacity-50"
            >
              スキップ
            </button>
          )}
        </div>
      )}
    </div>
  );
}
