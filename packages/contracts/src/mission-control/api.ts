import { z } from "zod";
import { QueryFiltersSchema } from "./filters.js";
import { ActivityEventSchema } from "./activity.js";
import { RunSummarySchema } from "./run.js";
import { WidgetConfigSchema } from "./widgets.js";
import { GridLayoutConfigSchema } from "./layout.js";
import { EvidenceRefSchema } from "./evidence.js";
import { SeveritySchema } from "./shared.js";

export const ApiMetaSchema = z
  .object({
    requestId: z.string().regex(/^req_[a-z0-9][a-z0-9-]{5,63}$/),
    generatedAt: z.string().datetime({ offset: true }),
    contractVersion: z.string().min(1)
  })
  .strict();

export const RunsQueryRequestSchema = z
  .object({
    filters: QueryFiltersSchema.default({
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
    })
  })
  .strict();

export const RunsQueryResponseSchema = z
  .object({
    meta: ApiMetaSchema,
    items: z.array(RunSummarySchema),
    total: z.number().int().min(0),
    page: z.number().int().min(1),
    pageSize: z.number().int().min(1)
  })
  .strict()
  .superRefine((value, ctx) => {
    if (value.items.length > value.pageSize) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["items"],
        message: "items length cannot exceed pageSize"
      });
    }
  });

export const ActivityQueryRequestSchema = z
  .object({
    cursor: z.string().nullable().default(null),
    limit: z.number().int().min(1).max(200).default(50),
    severities: z.array(SeveritySchema).default([])
  })
  .strict();

export const ActivityQueryResponseSchema = z
  .object({
    meta: ApiMetaSchema,
    items: z.array(ActivityEventSchema),
    cursor: z.string().nullable(),
    hasMore: z.boolean()
  })
  .strict();

export const WidgetsQueryRequestSchema = z
  .object({
    includeHidden: z.boolean().default(false),
    includeLayout: z.boolean().default(true)
  })
  .strict();

export const WidgetsQueryResponseSchema = z
  .object({
    meta: ApiMetaSchema,
    widgets: z.array(WidgetConfigSchema),
    layout: GridLayoutConfigSchema.nullable().default(null)
  })
  .strict();

export const EvidenceQueryRequestSchema = z
  .object({
    runId: z.string().regex(/^run_[a-z0-9][a-z0-9-]{3,63}$/),
    kinds: z
      .array(z.enum(["log", "artifact", "trace", "screenshot", "report", "metric-snapshot"]))
      .max(12)
      .default([]),
    limit: z.number().int().min(1).max(200).default(50)
  })
  .strict();

export const EvidenceQueryResponseSchema = z
  .object({
    meta: ApiMetaSchema,
    items: z.array(EvidenceRefSchema),
    total: z.number().int().min(0)
  })
  .strict();

export type RunsQueryRequest = z.infer<typeof RunsQueryRequestSchema>;
export type RunsQueryResponse = z.infer<typeof RunsQueryResponseSchema>;
export type ActivityQueryRequest = z.infer<typeof ActivityQueryRequestSchema>;
export type ActivityQueryResponse = z.infer<typeof ActivityQueryResponseSchema>;
export type WidgetsQueryRequest = z.infer<typeof WidgetsQueryRequestSchema>;
export type WidgetsQueryResponse = z.infer<typeof WidgetsQueryResponseSchema>;
export type EvidenceQueryRequest = z.infer<typeof EvidenceQueryRequestSchema>;
export type EvidenceQueryResponse = z.infer<typeof EvidenceQueryResponseSchema>;

export function createApiMeta(input: {
  requestId: string;
  generatedAt: string;
  contractVersion: string;
}): z.infer<typeof ApiMetaSchema> {
  return ApiMetaSchema.parse(input);
}
