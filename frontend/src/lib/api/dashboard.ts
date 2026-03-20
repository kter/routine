import { apiClient } from "./client";
import { mapDashboardDataDto } from "@/features/dashboard";
import type { DashboardDataDto } from "@/lib/api/dto/dashboard";

export const dashboardApi = {
  get: async () =>
    mapDashboardDataDto(
      await apiClient.get<DashboardDataDto>("/api/v1/dashboard"),
    ),
};
