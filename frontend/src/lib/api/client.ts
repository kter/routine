import { getIdToken } from "@/lib/auth/cognito";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// camelCase → snake_case
function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

function convertKeysToSnake(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(convertKeysToSnake);
  if (obj !== null && typeof obj === "object") {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
        toSnakeCase(k),
        convertKeysToSnake(v),
      ]),
    );
  }
  return obj;
}

// snake_case → camelCase
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function convertKeysToCamel(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(convertKeysToCamel);
  if (obj !== null && typeof obj === "object") {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
        toCamelCase(k),
        convertKeysToCamel(v),
      ]),
    );
  }
  return obj;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: unknown,
  ) {
    super(message);
  }
}

function extractErrorMessage(body: unknown): string | null {
  if (!body || typeof body !== "object") {
    return null;
  }

  const detail = (body as Record<string, unknown>).detail;
  if (typeof detail === "string" && detail.trim() !== "") {
    return detail;
  }

  const message = (body as Record<string, unknown>).message;
  if (typeof message === "string" && message.trim() !== "") {
    return message;
  }

  return null;
}

export function getApiErrorMessage(body: unknown, status: number): string {
  return extractErrorMessage(body) ?? `HTTP ${status}`;
}

export function normalizeApiError(
  error: unknown,
  fallbackMessage: string,
): Error {
  if (error instanceof ApiError) {
    return new Error(getApiErrorMessage(error.body, error.status));
  }

  if (error instanceof Error) {
    return error;
  }

  return new Error(fallbackMessage);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getIdToken();
  const url = `${BASE_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      response.status,
      getApiErrorMessage(body, response.status),
      body,
    );
  }

  if (response.status === 204) return undefined as T;
  const json = await response.json();
  return convertKeysToCamel(json) as T;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "POST",
      body: JSON.stringify(convertKeysToSnake(body)),
    }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "PUT",
      body: JSON.stringify(convertKeysToSnake(body)),
    }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: JSON.stringify(convertKeysToSnake(body)),
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
