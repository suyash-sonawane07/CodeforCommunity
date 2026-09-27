"use client";

/**
 * Minimal data-fetching hook with the three UI states every PRD screen needs
 * (loading / error / data — PRD §8.1). Deliberately dependency-free (no
 * react-query) until the team wants it.
 */
import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";

export interface ApiState<T> {
  data: T | null;
  error: ApiError | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[] = []): ApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    fetcher()
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e: unknown) => {
        if (!cancelled && e instanceof ApiError) setError(e);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);
  return { data, error, isLoading, refetch };
}
