import { useState, useEffect } from "react";
import { dashboardApi } from "@/lib/api/dashboard";
import type { DashboardData } from "../types";

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardApi.get();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch dashboard"));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  return { data, isLoading, error, refetch: fetch };
}
