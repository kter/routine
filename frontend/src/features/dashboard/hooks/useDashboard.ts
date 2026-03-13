import { useCallback } from "react";
import { dashboardApi } from "@/lib/api/dashboard";
import { useApiResource } from "@/lib/hooks/useApiResource";
import type { DashboardData } from "../types";

export function useDashboard() {
  const fetchDashboard = useCallback(() => dashboardApi.get(), []);
  const { data, isLoading, error, refetch } =
    useApiResource<DashboardData | null>(fetchDashboard, {
      initialData: null,
      errorMessage: "Failed to fetch dashboard",
    });

  return { data, isLoading, error, refetch };
}
