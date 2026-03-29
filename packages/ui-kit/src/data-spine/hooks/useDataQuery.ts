"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createStableQueryKey } from "../spine.js";
import type { DataSpine, Query, Result } from "../types.js";

interface CachedValue {
  readonly value: Result<unknown>;
  readonly updatedAt: number;
}

const QUERY_CACHE = new Map<string, CachedValue>();

export interface UseDataQueryOptions<TData = unknown> {
  readonly spine: DataSpine;
  readonly query: Query;
  readonly enabled?: boolean;
  readonly staleMs?: number;
  readonly keepPreviousData?: boolean;
  readonly initialData?: Result<TData>;
}

export interface UseDataQueryState<TData = unknown> {
  readonly key: string;
  readonly data: Result<TData> | undefined;
  readonly error: Error | undefined;
  readonly isLoading: boolean;
  readonly isFetching: boolean;
  refetch: (forceRefresh?: boolean) => Promise<Result<TData> | undefined>;
}

function readFreshCache<TData>(key: string, staleMs: number): Result<TData> | undefined {
  const cached = QUERY_CACHE.get(key);
  if (cached === undefined) {
    return undefined;
  }

  if (Date.now() - cached.updatedAt > staleMs) {
    return undefined;
  }

  return cached.value as Result<TData>;
}

export function useDataQuery<TData = unknown>(
  input: UseDataQueryOptions<TData>
): UseDataQueryState<TData> {
  const enabled = input.enabled ?? true;
  const staleMs = input.staleMs ?? 30_000;
  const keepPreviousData = input.keepPreviousData ?? true;

  const key = useMemo(() => createStableQueryKey(input.query), [input.query]);

  const queryRef = useRef(input.query);
  const requestRef = useRef(0);
  const mountedRef = useRef(true);

  const initialFromCache = readFreshCache<TData>(key, staleMs);

  const [data, setData] = useState<Result<TData> | undefined>(
    input.initialData ?? initialFromCache
  );
  const [error, setError] = useState<Error | undefined>(undefined);
  const [isFetching, setIsFetching] = useState(false);
  const [isLoading, setIsLoading] = useState(data === undefined && enabled);

  useEffect(() => {
    queryRef.current = input.query;
  }, [input.query]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    const cached = readFreshCache<TData>(key, staleMs);
    if (cached !== undefined) {
      setData(cached);
      setError(undefined);
      setIsLoading(false);
      return;
    }

    if (!enabled && !keepPreviousData) {
      setData(undefined);
      setError(undefined);
      setIsLoading(false);
    }
  }, [enabled, keepPreviousData, key, staleMs]);

  const refetch = useCallback(
    async (forceRefresh = false): Promise<Result<TData> | undefined> => {
      if (!enabled && !forceRefresh) {
        return data;
      }

      const localRequestId = requestRef.current + 1;
      requestRef.current = localRequestId;

      const hasData = readFreshCache<TData>(key, staleMs) ?? data;
      setIsFetching(true);
      setIsLoading(hasData === undefined);
      setError(undefined);

      const controller = new AbortController();

      try {
        const result = await input.spine.query<TData>({
          ...queryRef.current,
          signal: queryRef.current.signal ?? controller.signal,
          forceRefresh: forceRefresh || queryRef.current.forceRefresh === true
        });

        QUERY_CACHE.set(key, {
          value: result,
          updatedAt: Date.now()
        });

        if (!mountedRef.current || requestRef.current !== localRequestId) {
          return result;
        }

        setData(result);
        setIsLoading(false);
        setIsFetching(false);
        return result;
      } catch (reason) {
        if (!mountedRef.current || requestRef.current !== localRequestId) {
          return undefined;
        }

        setIsLoading(false);
        setIsFetching(false);
        setError(reason instanceof Error ? reason : new Error(String(reason)));
        if (!keepPreviousData) {
          setData(undefined);
        }
        return undefined;
      } finally {
        controller.abort();
      }
    },
    [data, enabled, input.spine, keepPreviousData, key, staleMs]
  );

  useEffect(() => {
    if (!enabled) {
      setIsLoading(false);
      setIsFetching(false);
      return;
    }

    const cached = readFreshCache<TData>(key, staleMs);
    if (cached !== undefined) {
      setData(cached);
      setError(undefined);
      setIsLoading(false);
      setIsFetching(false);
      return;
    }

    void refetch(false);
  }, [enabled, key, refetch, staleMs]);

  return {
    key,
    data,
    error,
    isLoading,
    isFetching,
    refetch
  };
}

