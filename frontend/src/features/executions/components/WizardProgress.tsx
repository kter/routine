import { Check, Minus } from "lucide-react";
import type { ExecutionStep } from "../types";

interface WizardProgressProps {
  steps: ExecutionStep[];
  currentIndex: number;
}

export function WizardProgress({ steps, currentIndex }: WizardProgressProps) {
  return (
    <div className="flex items-center gap-1">
      {steps.map((step, index) => {
        const isCompleted = step.status === "completed";
        const isSkipped = step.status === "skipped";
        const isCurrent = index === currentIndex && step.status === "pending";
        const isPast = index < currentIndex;

        let circleStyle: React.CSSProperties;
        if (isCompleted) {
          circleStyle = {
            background: "hsl(160 60% 45%)",
            border: "2px solid hsl(160 60% 45%)",
            color: "hsl(222 47% 5%)",
          };
        } else if (isSkipped) {
          circleStyle = {
            background: "hsl(218 28% 16%)",
            border: "2px solid hsl(218 28% 24%)",
            color: "hsl(215 16% 44%)",
          };
        } else if (isCurrent) {
          circleStyle = {
            background: "hsl(43 96% 56%)",
            border: "2px solid hsl(43 96% 56%)",
            color: "hsl(222 47% 5%)",
          };
        } else {
          circleStyle = {
            background: "hsl(218 28% 12%)",
            border: "2px solid hsl(218 28% 20%)",
            color: "hsl(215 16% 38%)",
          };
        }

        const connectorColor =
          isPast || isCompleted ? "hsl(160 60% 35%)" : "hsl(218 28% 18%)";

        return (
          <div key={step.id} className="flex items-center">
            <div
              className="flex h-6 w-6 items-center justify-center rounded-full font-mono-data text-[10px] font-500 transition-all duration-200"
              style={circleStyle}
            >
              {isCompleted ? (
                <Check className="h-3 w-3" strokeWidth={2.5} />
              ) : isSkipped ? (
                <Minus className="h-3 w-3" strokeWidth={2.5} />
              ) : (
                index + 1
              )}
            </div>
            {index < steps.length - 1 && (
              <div
                className="h-px w-5 transition-colors duration-200"
                style={{ background: connectorColor }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
