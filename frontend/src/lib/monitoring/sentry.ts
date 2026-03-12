import { useEffect } from "react";
import * as Sentry from "@sentry/react";
import {
  createBrowserRouter,
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from "react-router-dom";
import { getSentryRuntimeConfig } from "./sentryOptions";

const sentryConfig = getSentryRuntimeConfig({
  MODE: import.meta.env.MODE,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  VITE_SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
  VITE_SENTRY_ENVIRONMENT: import.meta.env.VITE_SENTRY_ENVIRONMENT,
  VITE_SENTRY_TRACES_SAMPLE_RATE: import.meta.env
    .VITE_SENTRY_TRACES_SAMPLE_RATE,
});

if (sentryConfig) {
  Sentry.init({
    dsn: sentryConfig.dsn,
    environment: sentryConfig.environment,
    integrations: [
      Sentry.reactRouterV7BrowserTracingIntegration({
        createRoutesFromChildren,
        matchRoutes,
        useEffect,
        useLocation,
        useNavigationType,
      }),
    ],
    tracePropagationTargets: sentryConfig.tracePropagationTargets,
    tracesSampleRate: sentryConfig.tracesSampleRate,
  });
}

export const createAppRouter = sentryConfig
  ? Sentry.wrapCreateBrowserRouterV7(createBrowserRouter)
  : createBrowserRouter;
