import { apiClient } from "./client";
import type { DashboardData } from "@/features/dashboard/types";

export const dashboardApi = {
  get: () => apiClient.get<DashboardData>("/api/v1/dashboard"),
};
