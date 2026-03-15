import { apiClient } from "./client";
import type { TaskInput, TaskUpdateInput } from "@/features/tasks/types";
import type { TaskDto } from "@/lib/api/dto/tasks";
import {
  mapTaskDto,
  toCreateTaskRequestDto,
  toUpdateTaskRequestDto,
} from "@/features/tasks/mappers";

export const tasksApi = {
  list: async () =>
    (await apiClient.get<TaskDto[]>("/api/v1/tasks")).map(mapTaskDto),
  get: async (id: string) =>
    mapTaskDto(await apiClient.get<TaskDto>(`/api/v1/tasks/${id}`)),
  create: async (data: TaskInput) =>
    mapTaskDto(
      await apiClient.post<TaskDto>(
        "/api/v1/tasks",
        toCreateTaskRequestDto(data),
      ),
    ),
  update: async (id: string, data: TaskUpdateInput) =>
    mapTaskDto(
      await apiClient.patch<TaskDto>(
        `/api/v1/tasks/${id}`,
        toUpdateTaskRequestDto(data),
      ),
    ),
  delete: (id: string) => apiClient.delete<void>(`/api/v1/tasks/${id}`),
};
