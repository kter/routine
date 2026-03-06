import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(isoString: string): string {
  const d = new Date(isoString);
  return new Intl.DateTimeFormat("ja-JP", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}

const CRON_DESCRIPTIONS: Record<string, string> = {
  "0 10 * * *": "毎日 10:00",
  "0 10 * * 1": "毎週月曜 10:00",
  "0 10 1 * *": "毎月1日 10:00",
  "0 9 * * 1-5": "平日 9:00",
  "0 0 * * *": "毎日 0:00",
};

export function formatCron(expression: string): string {
  return CRON_DESCRIPTIONS[expression] ?? expression;
}
