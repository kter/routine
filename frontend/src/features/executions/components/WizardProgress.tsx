import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ExecutionStep } from "../types";

interface WizardProgressProps {
  steps: ExecutionStep[];
  currentIndex: number;
}

export function WizardProgress({ steps, currentIndex }: WizardProgressProps) {
  return (
    <div className="flex items-center gap-1">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <div
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-full border-2 text-xs font-medium transition-colors",
              step.status === "completed"
                ? "border-green-500 bg-green-500 text-white"
                : step.status === "skipped"
                  ? "border-muted-foreground bg-muted text-muted-foreground"
                  : index === currentIndex
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background text-muted-foreground",
            )}
          >
            {step.status === "completed" ? (
              <Check className="h-3.5 w-3.5" />
            ) : (
              index + 1
            )}
          </div>
          {index < steps.length - 1 && (
            <div
              className={cn(
                "h-0.5 w-6",
                index < currentIndex ? "bg-green-500" : "bg-border",
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}
