"use client";

import { useEffect, useMemo } from "react";
import { useDataQuery, type UseDataQueryOptions, type UseDataQueryState } from "./useDataQuery.js";
import type { PerfProfile, Result } from "../types.js";

const DEFAULT_INTERVAL_MS = 15_000;
const PERF_INTERVAL_FLOOR_MS = 60_000;

export interface UseLiveDataOptions<TData = unknown> extends UseDataQueryOptions<TData> {
  readonly pollIntervalMs?: number;
  readonly perfProfile?: PerfProfile;
  readonly enablePollingInPerf?: boolean;
}

export interface PollingPlan {
  readonly enabled: boolean;
  readonly intervalMs: number | null;
  readonly reason: string;
}

export interface UseLiveDataState<TData = unknown> extends UseDataQueryState<TData> {
  readonly pollingPlan: PollingPlan;
  readonly latest: Result<TData> | undefined;
}

export function createPollingPlan(input: {
  readonly enabled: boolean;
  readonly pollIntervalMs: number | undefined;
  readonly perfProfile: PerfProfile;
  readonly enablePollingInPerf: boolean;
}): PollingPlan {
  if (!input.enabled) {
    return {
      enabled: false,
      intervalMs: null,
      reason: "query-disabled"
    };
  }

  if (input.perfProfile === "perf" && !input.enablePollingInPerf) {
    return {
      enabled: false,
      intervalMs: null,
      reason: "perf-profile-disabled"
    };
  }

  const requested = input.pollIntervalMs ?? DEFAULT_INTERVAL_MS;

  if (input.perfProfile === "perf") {
    return {
      enabled: true,
      intervalMs: Math.max(PERF_INTERVAL_FLOOR_MS, requested),
      reason: "perf-profile-low-frequency"
    };
  }

  return {
    enabled: true,
    intervalMs: Math.max(1_000, requested),
    reason: "default"
  };
}

export function useLiveData<TData = unknown>(input: UseLiveDataOptions<TData>): UseLiveDataState<TData> {
  const perfProfile = input.perfProfile ?? input.query.perfProfile ?? "default";
  const enablePollingInPerf = input.enablePollingInPerf ?? false;

  const enrichedQuery = useMemo(
    () => ({
      ...input.query,
      perfProfile: input.query.perfProfile ?? perfProfile
    }),
    [input.query, perfProfile]
  );

  const queryState = useDataQuery<TData>({
    ...input,
    query: enrichedQuery
  });

  const pollingPlan = useMemo(
    () =>
      createPollingPlan({
        enabled: input.enabled ?? true,
        pollIntervalMs: input.pollIntervalMs,
        perfProfile,
        enablePollingInPerf
      }),
    [enablePollingInPerf, input.enabled, input.pollIntervalMs, perfProfile]
  );

  useEffect(() => {
    if (!pollingPlan.enabled || pollingPlan.intervalMs === null) {
      return;
    }

    const timer = setInterval(() => {
      void queryState.refetch(true);
    }, pollingPlan.intervalMs);

    return () => {
      clearInterval(timer);
    };
  }, [pollingPlan.enabled, pollingPlan.intervalMs, queryState.refetch]);

  return {
    ...queryState,
    pollingPlan,
    latest: queryState.data
  };
}


