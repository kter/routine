import { apiClient } from "./client";
import type { DashboardDataDto } from "@/lib/api/dto/dashboard";
import { mapDashboardDataDto } from "@/features/dashboard/mappers";

export const dashboardApi = {
  get: async () =>
    mapDashboardDataDto(
      await apiClient.get<DashboardDataDto>("/api/v1/dashboard"),
    ),
};
