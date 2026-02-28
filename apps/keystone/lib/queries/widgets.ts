"use client";

import { WidgetsQueryResponseSchema, type WidgetsQueryResponse } from "@hitech/contracts";
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { fetchContract } from "../api/http";

export const widgetsQueryKey = ["keystone", "widgets"] as const;

export function useWidgetsQuery(): UseQueryResult<WidgetsQueryResponse> {
  return useQuery({
    queryKey: widgetsQueryKey,
    queryFn: () =>
      fetchContract({
        path: "/api/widgets",
        schema: WidgetsQueryResponseSchema,
        resource: "api.widgets"
      })
  });
}
