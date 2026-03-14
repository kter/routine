import { normalizeApiError } from "@/lib/api/client";

export function getQueryError(
  error: unknown,
  fallbackMessage: string,
): Error | null {
  if (!error) {
    return null;
  }

  return normalizeApiError(error, fallbackMessage);
}
