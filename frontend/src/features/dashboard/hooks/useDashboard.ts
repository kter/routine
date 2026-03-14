import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/lib/api/dashboard";
import { getQueryError } from "@/lib/query/queryError";
import { queryKeys } from "@/lib/query/queryKeys";
import type { DashboardData } from "../types";

export function useDashboard() {
  const query = useQuery<DashboardData>({
    queryKey: queryKeys.dashboard,
    queryFn: dashboardApi.get,
  });

  return {
    data: query.data ?? null,
    isLoading: query.isPending,
    error: getQueryError(query.error, "Failed to fetch dashboard"),
    refetch: query.refetch,
  };
}
