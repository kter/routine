import { useCallback, useEffect, useState } from "react";
import { normalizeApiError } from "@/lib/api/client";

type UseApiResourceOptions<T> = {
  initialData: T;
  errorMessage: string;
  enabled?: boolean;
};

export function useApiResource<T>(
  fetcher: () => Promise<T>,
  options: UseApiResourceOptions<T>,
) {
  const [data, setData] = useState<T>(options.initialData);
  const [isLoading, setIsLoading] = useState(options.enabled !== false);
  const [error, setError] = useState<Error | null>(null);

  const refetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
      return result;
    } catch (err) {
      const normalizedError = normalizeApiError(err, options.errorMessage);
      setError(normalizedError);
      return undefined;
    } finally {
      setIsLoading(false);
    }
  }, [fetcher, options.errorMessage]);

  useEffect(() => {
    if (options.enabled === false) {
      setIsLoading(false);
      return;
    }

    void refetch();
  }, [options.enabled, refetch]);

  return { data, setData, isLoading, error, refetch };
}
