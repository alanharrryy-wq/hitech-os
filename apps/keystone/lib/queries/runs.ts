"use client";

import { RunsQueryResponseSchema, type RunsQueryResponse } from "@hitech/contracts";
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { fetchContract } from "../api/http";

export const runsQueryKey = ["keystone", "runs"] as const;

export function useRunsQuery(): UseQueryResult<RunsQueryResponse> {
  return useQuery({
    queryKey: runsQueryKey,
    queryFn: () =>
      fetchContract({
        path: "/api/runs",
        schema: RunsQueryResponseSchema,
        resource: "api.runs"
      })
  });
}
