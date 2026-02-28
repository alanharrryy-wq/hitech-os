import { z } from "zod";
import { RunStatusSchema } from "./run.js";
import { SeveritySchema } from "./shared.js";

export const SortDirectionSchema = z.enum(["asc", "desc"]);

export const SortFieldSchema = z.enum([
  "createdAt",
  "updatedAt",
  "finishedAt",
  "name",
  "status",
  "priority",
  "severity"
]);

export const SortSchema = z
  .object({
    field: SortFieldSchema,
    direction: SortDirectionSchema.default("desc")
  })
  .strict();

export const PaginationRequestSchema = z
  .object({
    page: z.number().int().min(1).default(1),
    pageSize: z.number().int().min(1).max(200).default(25)
  })
  .strict();

export const AbsoluteTimeRangeSchema = z
  .object({
    type: z.literal("absolute"),
    from: z.string().datetime({ offset: true }),
    to: z.string().datetime({ offset: true })
  })
  .strict();

export const RelativeTimeUnitSchema = z.enum(["minutes", "hours", "days", "weeks"]);

export const RelativeTimeRangeSchema = z
  .object({
    type: z.literal("relative"),
    amount: z.number().int().min(1).max(365),
    unit: RelativeTimeUnitSchema
  })
  .strict();

export const TimeRangeSchema = z.discriminatedUnion("type", [
  AbsoluteTimeRangeSchema,
  RelativeTimeRangeSchema
]);

export const QueryFiltersSchema = z
  .object({
    search: z.string().trim().max(200).default(""),
    statuses: z.array(RunStatusSchema).max(16).default([]),
    severities: z.array(SeveritySchema).max(8).default([]),
    owners: z.array(z.string().min(1).max(120)).max(64).default([]),
    tags: z.array(z.string().min(1).max(64)).max(64).default([]),
    timeRange: TimeRangeSchema.nullable().default(null),
    sort: SortSchema.default({ field: "updatedAt", direction: "desc" }),
    pagination: PaginationRequestSchema.default({ page: 1, pageSize: 25 })
  })
  .strict()
  .superRefine((value, ctx) => {
    if (
      value.timeRange &&
      value.timeRange.type === "absolute" &&
      Date.parse(value.timeRange.to) < Date.parse(value.timeRange.from)
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["timeRange", "to"],
        message: "timeRange.to must be greater than or equal to timeRange.from"
      });
    }
  });

export type SortDirection = z.infer<typeof SortDirectionSchema>;
export type SortField = z.infer<typeof SortFieldSchema>;
export type Sort = z.infer<typeof SortSchema>;
export type PaginationRequest = z.infer<typeof PaginationRequestSchema>;
export type AbsoluteTimeRange = z.infer<typeof AbsoluteTimeRangeSchema>;
export type RelativeTimeRange = z.infer<typeof RelativeTimeRangeSchema>;
export type TimeRange = z.infer<typeof TimeRangeSchema>;
export type QueryFilters = z.infer<typeof QueryFiltersSchema>;

export const DEFAULT_QUERY_FILTERS: QueryFilters = {
  search: "",
  statuses: [],
  severities: [],
  owners: [],
  tags: [],
  timeRange: null,
  sort: {
    field: "updatedAt",
    direction: "desc"
  },
  pagination: {
    page: 1,
    pageSize: 25
  }
};

export function resolveQueryFilters(input?: Partial<QueryFilters>): QueryFilters {
  return QueryFiltersSchema.parse({
    ...DEFAULT_QUERY_FILTERS,
    ...(input ?? {}),
    sort: {
      ...DEFAULT_QUERY_FILTERS.sort,
      ...(input?.sort ?? {})
    },
    pagination: {
      ...DEFAULT_QUERY_FILTERS.pagination,
      ...(input?.pagination ?? {})
    }
  });
}

export function getRelativeRangeAnchor(
  nowIso: string,
  range: RelativeTimeRange
): {
  readonly from: string;
  readonly to: string;
} {
  const now = new Date(nowIso);
  const from = new Date(now.getTime());

  const multipliers: Record<RelativeTimeRange["unit"], number> = {
    minutes: 60_000,
    hours: 3_600_000,
    days: 86_400_000,
    weeks: 604_800_000
  };

  from.setTime(now.getTime() - multipliers[range.unit] * range.amount);

  return {
    from: from.toISOString(),
    to: now.toISOString()
  };
}
