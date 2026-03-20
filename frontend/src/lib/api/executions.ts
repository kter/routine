import { apiClient } from "./client";
import type {
  CompleteStepInput,
  StartExecutionInput,
} from "@/features/executions";
import type { ExecutionDto } from "@/lib/api/dto/executions";
import {
  mapExecutionDto,
  toCompleteStepRequestDto,
  toStartExecutionRequestDto,
} from "@/features/executions";

export const executionsApi = {
  list: async () =>
    (await apiClient.get<ExecutionDto[]>("/api/v1/executions")).map(
      mapExecutionDto,
    ),
  get: async (id: string) =>
    mapExecutionDto(
      await apiClient.get<ExecutionDto>(`/api/v1/executions/${id}`),
    ),
  start: async (data: StartExecutionInput) =>
    mapExecutionDto(
      await apiClient.post<ExecutionDto>(
        "/api/v1/executions",
        toStartExecutionRequestDto(data),
      ),
    ),
  completeStep: (
    executionId: string,
    stepId: string,
    data: CompleteStepInput,
  ) =>
    apiClient.patch<void>(
      `/api/v1/executions/${executionId}/steps/${stepId}/complete`,
      toCompleteStepRequestDto(data),
    ),
  skipStep: (executionId: string, stepId: string) =>
    apiClient.patch<void>(
      `/api/v1/executions/${executionId}/steps/${stepId}/skip`,
      {},
    ),
  complete: async (id: string, data: { notes?: string }) =>
    mapExecutionDto(
      await apiClient.patch<ExecutionDto>(
        `/api/v1/executions/${id}/complete`,
        data,
      ),
    ),
  abandon: async (id: string, data: { notes?: string }) =>
    mapExecutionDto(
      await apiClient.patch<ExecutionDto>(
        `/api/v1/executions/${id}/abandon`,
        data,
      ),
    ),
  getEvidenceUploadUrl: (
    executionId: string,
    stepId: string,
    contentType: string,
  ): Promise<{ uploadUrl: string; key: string }> =>
    apiClient.post(
      `/api/v1/executions/${executionId}/steps/${stepId}/evidence-url`,
      {
        contentType,
      },
    ),
};
