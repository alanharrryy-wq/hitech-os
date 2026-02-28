"use client";

import { ActivityQueryResponseSchema, type ActivityQueryResponse } from "@hitech/contracts";
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { fetchContract } from "../api/http";

export const activityQueryKey = ["keystone", "activity"] as const;

export function useActivityQuery(): UseQueryResult<ActivityQueryResponse> {
  return useQuery({
    queryKey: activityQueryKey,
    queryFn: () =>
      fetchContract({
        path: "/api/activity",
        schema: ActivityQueryResponseSchema,
        resource: "api.activity"
      })
  });
}
