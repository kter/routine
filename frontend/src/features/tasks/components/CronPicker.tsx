import { useState } from "react";
import { formatCron } from "@/lib/utils";

interface CronPickerProps {
  value: string;
  onChange: (value: string) => void;
}

const PRESETS = [
  { label: "毎日 10:00", value: "0 10 * * *" },
  { label: "毎週月曜 10:00", value: "0 10 * * 1" },
  { label: "毎月1日 10:00", value: "0 10 1 * *" },
  { label: "毎月末日 10:00", value: "0 10 L * *" },
  { label: "カスタム", value: "custom" },
];

export function CronPicker({ value, onChange }: CronPickerProps) {
  const isPreset = PRESETS.some((p) => p.value === value && p.value !== "custom");
  const [mode, setMode] = useState<"preset" | "custom">(isPreset ? "preset" : "custom");

  const handlePresetChange = (preset: string) => {
    if (preset === "custom") {
      setMode("custom");
    } else {
      setMode("preset");
      onChange(preset);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.value}
            type="button"
            onClick={() => handlePresetChange(p.value)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              (p.value === "custom" && mode === "custom") ||
              (p.value === value && mode === "preset")
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-accent"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
      {mode === "custom" && (
        <div className="space-y-1">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="例: 0 10 * * *"
            className="w-full rounded border bg-background px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-ring"
          />
          {value && (
            <p className="text-xs text-muted-foreground">{formatCron(value)}</p>
          )}
        </div>
      )}
    </div>
  );
}
