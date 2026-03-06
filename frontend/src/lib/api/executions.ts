import { apiClient } from "./client";
import type {
  Execution,
  StartExecutionRequest,
  CompleteStepRequest,
} from "@/features/executions/types";

export const executionsApi = {
  list: () => apiClient.get<Execution[]>("/api/v1/executions"),
  get: (id: string) => apiClient.get<Execution>(`/api/v1/executions/${id}`),
  start: (data: StartExecutionRequest) =>
    apiClient.post<Execution>("/api/v1/executions", data),
  completeStep: (executionId: string, stepId: string, data: CompleteStepRequest) =>
    apiClient.patch<void>(
      `/api/v1/executions/${executionId}/steps/${stepId}/complete`,
      data,
    ),
  skipStep: (executionId: string, stepId: string) =>
    apiClient.patch<void>(
      `/api/v1/executions/${executionId}/steps/${stepId}/skip`,
      {},
    ),
  complete: (id: string, data: { notes?: string }) =>
    apiClient.patch<Execution>(`/api/v1/executions/${id}/complete`, data),
  abandon: (id: string, data: { notes?: string }) =>
    apiClient.patch<Execution>(`/api/v1/executions/${id}/abandon`, data),
  getEvidenceUploadUrl: (
    executionId: string,
    stepId: string,
    contentType: string,
  ): Promise<{ uploadUrl: string; key: string }> =>
    apiClient.post(`/api/v1/executions/${executionId}/steps/${stepId}/evidence-url`, {
      contentType,
    }),
};
