import { Plus, Trash2, GripVertical } from "lucide-react";
import type { CreateStepRequest } from "../types";

interface StepEditorProps {
  steps: CreateStepRequest[];
  onChange: (steps: CreateStepRequest[]) => void;
}

export function StepEditor({ steps, onChange }: StepEditorProps) {
  const addStep = () => {
    onChange([
      ...steps,
      {
        position: steps.length + 1,
        title: "",
        instruction: "",
        evidenceType: "none",
        isRequired: true,
      },
    ]);
  };

  const updateStep = (index: number, field: keyof CreateStepRequest, value: unknown) => {
    const updated = steps.map((s, i) => (i === index ? { ...s, [field]: value } : s));
    onChange(updated);
  };

  const removeStep = (index: number) => {
    const updated = steps
      .filter((_, i) => i !== index)
      .map((s, i) => ({ ...s, position: i + 1 }));
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      {steps.map((step, index) => (
        <div key={index} className="flex gap-2 rounded-md border p-3">
          <GripVertical className="mt-2 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">
                ステップ {step.position}
              </span>
            </div>
            <input
              type="text"
              placeholder="ステップタイトル"
              value={step.title}
              onChange={(e) => updateStep(index, "title", e.target.value)}
              className="w-full rounded border bg-background px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <textarea
              placeholder="手順の説明（Markdown対応）"
              value={step.instruction}
              onChange={(e) => updateStep(index, "instruction", e.target.value)}
              rows={2}
              className="w-full rounded border bg-background px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-1.5 text-xs">
                <span className="text-muted-foreground">証跡タイプ:</span>
                <select
                  value={step.evidenceType}
                  onChange={(e) => updateStep(index, "evidenceType", e.target.value)}
                  className="rounded border bg-background px-1 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                >
                  <option value="none">なし</option>
                  <option value="text">テキスト</option>
                  <option value="image">画像</option>
                </select>
              </label>
              <label className="flex items-center gap-1.5 text-xs">
                <input
                  type="checkbox"
                  checked={step.isRequired}
                  onChange={(e) => updateStep(index, "isRequired", e.target.checked)}
                  className="h-3 w-3"
                />
                <span>必須</span>
              </label>
            </div>
          </div>
          <button
            type="button"
            onClick={() => removeStep(index)}
            className="mt-1 self-start text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={addStep}
        className="flex w-full items-center justify-center gap-2 rounded-md border border-dashed py-2 text-sm text-muted-foreground hover:border-primary hover:text-primary"
      >
        <Plus className="h-4 w-4" />
        ステップを追加
      </button>
    </div>
  );
}
