import { useState } from "react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { EvidenceUpload } from "./EvidenceUpload";
import type { CompleteStepInput, ExecutionStep } from "../types";

interface StepPanelProps {
  step: ExecutionStep;
  onComplete: (req: CompleteStepInput) => Promise<void>;
  onSkip: () => Promise<void>;
}

export function StepPanel({ step, onComplete, onSkip }: StepPanelProps) {
  const [evidenceText, setEvidenceText] = useState("");
  const [evidenceImageKey, setEvidenceImageKey] = useState<
    string | undefined
  >();
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { title, instruction, evidenceType, isRequired } = step.stepSnapshot;

  const handleComplete = async () => {
    setIsSubmitting(true);
    try {
      await onComplete({
        evidenceText: evidenceType === "text" ? evidenceText : undefined,
        evidenceImageKey:
          evidenceType === "image" ? evidenceImageKey : undefined,
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

  const inputStyle: React.CSSProperties = {
    background: "hsl(218 30% 10%)",
    border: "1px solid hsl(218 28% 20%)",
    color: "hsl(210 20% 88%)",
    borderRadius: "0.375rem",
    outline: "none",
  };

  return (
    <div
      className="space-y-5 rounded-md p-5 animate-fade-up"
      style={{
        background: "hsl(220 40% 8%)",
        border: "1px solid hsl(218 28% 16%)",
        borderLeft: "3px solid hsl(43 96% 56%)",
      }}
    >
      <div>
        <h3
          className="font-brand text-base font-700 tracking-tight"
          style={{ color: "hsl(210 20% 90%)", fontWeight: 700 }}
        >
          {title}
        </h3>
        {instruction && (
          <div
            className="mt-3 text-sm leading-relaxed"
            style={{ color: "hsl(215 16% 55%)" }}
          >
            <MarkdownRenderer content={instruction} />
          </div>
        )}
      </div>

      {evidenceType === "text" && step.status === "pending" && (
        <div className="space-y-1.5">
          <label
            className="block font-mono-data text-[11px] uppercase tracking-widest"
            style={{ color: "hsl(215 16% 44%)" }}
          >
            証跡テキスト *
          </label>
          <textarea
            value={evidenceText}
            onChange={(e) => setEvidenceText(e.target.value)}
            rows={4}
            placeholder="実施内容や確認結果を入力してください"
            className="w-full px-3 py-2 text-sm resize-none focus:ring-1"
            style={
              {
                ...inputStyle,
                "--tw-ring-color": "hsl(43 96% 56%)",
              } as React.CSSProperties
            }
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

      <div className="space-y-1.5">
        <label
          className="block font-mono-data text-[11px] uppercase tracking-widest"
          style={{ color: "hsl(215 16% 38%)" }}
        >
          メモ（任意）
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          placeholder="補足事項があれば入力"
          className="w-full px-3 py-2 text-sm resize-none"
          style={inputStyle}
        />
      </div>

      {step.status === "pending" && (
        <div className="flex gap-3">
          <button
            onClick={handleComplete}
            disabled={!canComplete || isSubmitting}
            className="rounded px-5 py-2 text-sm font-medium transition-all duration-150 disabled:opacity-40"
            style={{
              color: "hsl(222 47% 5%)",
              background:
                canComplete && !isSubmitting
                  ? "hsl(43 96% 56%)"
                  : "hsl(43 60% 30%)",
            }}
          >
            {isSubmitting ? "処理中..." : "完了"}
          </button>
          {!isRequired && (
            <button
              onClick={onSkip}
              disabled={isSubmitting}
              className="rounded px-5 py-2 text-sm transition-all duration-150 disabled:opacity-40"
              style={{
                color: "hsl(215 16% 55%)",
                border: "1px solid hsl(218 28% 22%)",
              }}
            >
              スキップ
            </button>
          )}
        </div>
      )}
    </div>
  );
}
