import { useCallback, useEffect, useRef, useState } from "react";
import { normalizeApiError } from "@/lib/api/client";

type UseApiResourceOptions<T> = {
  initialData: T;
  errorMessage: string;
  enabled?: boolean;
};

type ResourceRequestSnapshot = {
  generation: number;
  requestId: number;
};

type ResourceRequestState = {
  currentGeneration: number;
  latestRequestId: number;
};

export function shouldApplyResourceResult(
  snapshot: ResourceRequestSnapshot,
  state: ResourceRequestState,
): boolean {
  return (
    snapshot.generation === state.currentGeneration &&
    snapshot.requestId === state.latestRequestId
  );
}

export function useApiResource<T>(
  fetcher: () => Promise<T>,
  options: UseApiResourceOptions<T>,
) {
  const fetcherRef = useRef(fetcher);
  const generationRef = useRef(0);
  if (fetcherRef.current !== fetcher) {
    fetcherRef.current = fetcher;
    generationRef.current += 1;
  }

  const [data, setData] = useState<T>(options.initialData);
  const [isLoading, setIsLoading] = useState(options.enabled !== false);
  const [error, setError] = useState<Error | null>(null);
  const latestRequestIdRef = useRef(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const refetch = useCallback(async () => {
    const requestId = latestRequestIdRef.current + 1;
    latestRequestIdRef.current = requestId;
    const snapshot = {
      generation: generationRef.current,
      requestId,
    };

    setIsLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      if (
        mountedRef.current &&
        shouldApplyResourceResult(snapshot, {
          currentGeneration: generationRef.current,
          latestRequestId: latestRequestIdRef.current,
        })
      ) {
        setData(result);
      }
      return result;
    } catch (err) {
      const normalizedError = normalizeApiError(err, options.errorMessage);
      if (
        mountedRef.current &&
        shouldApplyResourceResult(snapshot, {
          currentGeneration: generationRef.current,
          latestRequestId: latestRequestIdRef.current,
        })
      ) {
        setError(normalizedError);
      }
      return undefined;
    } finally {
      if (
        mountedRef.current &&
        shouldApplyResourceResult(snapshot, {
          currentGeneration: generationRef.current,
          latestRequestId: latestRequestIdRef.current,
        })
      ) {
        setIsLoading(false);
      }
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
