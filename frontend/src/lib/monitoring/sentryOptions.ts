export type TracePropagationTarget = RegExp | string;

export interface SentryRuntimeEnv {
  MODE?: string;
  VITE_API_BASE_URL?: string;
  VITE_SENTRY_DSN?: string;
  VITE_SENTRY_ENVIRONMENT?: string;
  VITE_SENTRY_TRACES_SAMPLE_RATE?: string;
}

export interface SentryRuntimeConfig {
  dsn: string;
  environment: string;
  tracePropagationTargets: TracePropagationTarget[];
  tracesSampleRate: number;
}

const DEFAULT_TRACES_SAMPLE_RATE = 0.1;

export function parseTracesSampleRate(value?: string): number {
  const parsed = Number(value);

  if (Number.isFinite(parsed) && parsed >= 0 && parsed <= 1) {
    return parsed;
  }

  return DEFAULT_TRACES_SAMPLE_RATE;
}

export function getTracePropagationTargets(
  apiBaseUrl?: string,
): TracePropagationTarget[] {
  return ["localhost", /^\/api/, ...(apiBaseUrl ? [apiBaseUrl] : [])];
}

export function getSentryRuntimeConfig(
  env: SentryRuntimeEnv,
): SentryRuntimeConfig | null {
  const dsn = env.VITE_SENTRY_DSN?.trim();

  if (!dsn) {
    return null;
  }

  return {
    dsn,
    environment:
      env.VITE_SENTRY_ENVIRONMENT?.trim() || env.MODE || "production",
    tracePropagationTargets: getTracePropagationTargets(env.VITE_API_BASE_URL),
    tracesSampleRate: parseTracesSampleRate(env.VITE_SENTRY_TRACES_SAMPLE_RATE),
  };
}
