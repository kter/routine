import { apiClient } from "./client";
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from "@/features/tasks/types";

export const tasksApi = {
  list: () => apiClient.get<Task[]>("/api/v1/tasks"),
  get: (id: string) => apiClient.get<Task>(`/api/v1/tasks/${id}`),
  create: (data: CreateTaskRequest) =>
    apiClient.post<Task>("/api/v1/tasks", data),
  update: (id: string, data: UpdateTaskRequest) =>
    apiClient.patch<Task>(`/api/v1/tasks/${id}`, data),
  delete: (id: string) => apiClient.delete<void>(`/api/v1/tasks/${id}`),
};
