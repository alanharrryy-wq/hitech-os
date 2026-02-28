import { z } from "zod";
import { WidgetIdSchema } from "../brands.js";

export const WidgetKindSchema = z.enum([
  "table",
  "stat",
  "chart-placeholder",
  "feed",
  "dial-placeholder"
]);

export const WidgetRefreshPolicySchema = z
  .object({
    mode: z.enum(["manual", "interval", "passive"]),
    intervalSeconds: z.number().int().min(5).max(3600).nullable().default(null)
  })
  .strict();

export const WidgetDensitySchema = z.enum(["compact", "comfortable", "spacious"]);

export const WidgetBaseSchema = z
  .object({
    id: WidgetIdSchema,
    kind: WidgetKindSchema,
    title: z.string().min(2).max(120),
    subtitle: z.string().max(160).nullable().default(null),
    description: z.string().max(400).nullable().default(null),
    refresh: WidgetRefreshPolicySchema,
    density: WidgetDensitySchema.default("comfortable"),
    pinned: z.boolean().default(false),
    hidden: z.boolean().default(false)
  })
  .strict();

export const TableColumnSchema = z
  .object({
    key: z.string().min(1).max(120),
    label: z.string().min(1).max(120),
    align: z.enum(["left", "center", "right"]).default("left"),
    width: z.number().int().min(40).max(600).nullable().default(null),
    sortable: z.boolean().default(true),
    truncation: z.enum(["none", "line", "char"]).default("line")
  })
  .strict();

export const TableWidgetConfigSchema = WidgetBaseSchema.extend({
  kind: z.literal("table"),
  config: z
    .object({
      columns: z.array(TableColumnSchema).min(1).max(32),
      rowKey: z.string().min(1).max(120),
      maxRows: z.number().int().min(1).max(500).default(50),
      striped: z.boolean().default(true),
      stickyHeader: z.boolean().default(true)
    })
    .strict()
});

export const StatWidgetConfigSchema = WidgetBaseSchema.extend({
  kind: z.literal("stat"),
  config: z
    .object({
      value: z.number(),
      unit: z.string().max(24).default(""),
      trend: z.enum(["up", "down", "flat"]).default("flat"),
      precision: z.number().int().min(0).max(6).default(0),
      sparkline: z.array(z.number()).max(128).default([])
    })
    .strict()
});

export const ChartPlaceholderWidgetConfigSchema = WidgetBaseSchema.extend({
  kind: z.literal("chart-placeholder"),
  config: z
    .object({
      chartFamily: z.enum(["line", "bar", "area", "heatmap", "donut"]),
      xLabel: z.string().max(64).default("time"),
      yLabel: z.string().max(64).default("value"),
      seriesNames: z.array(z.string().min(1).max(64)).min(1).max(12),
      supportsStacking: z.boolean().default(false)
    })
    .strict()
});

export const FeedWidgetConfigSchema = WidgetBaseSchema.extend({
  kind: z.literal("feed"),
  config: z
    .object({
      source: z.enum(["activity", "alerts", "audit", "custom"]),
      maxItems: z.number().int().min(1).max(250).default(25),
      showSeverity: z.boolean().default(true),
      compactTimestamps: z.boolean().default(true)
    })
    .strict()
});

export const DialPlaceholderWidgetConfigSchema = WidgetBaseSchema.extend({
  kind: z.literal("dial-placeholder"),
  config: z
    .object({
      min: z.number().default(0),
      max: z.number().default(100),
      value: z.number().default(0),
      warningThreshold: z.number().nullable().default(null),
      criticalThreshold: z.number().nullable().default(null),
      unit: z.string().max(24).default("%")
    })
    .strict()
    .superRefine((value, ctx) => {
      if (value.max <= value.min) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "max must be greater than min",
          path: ["max"]
        });
      }

      if (value.value < value.min || value.value > value.max) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "value must be inside [min, max]",
          path: ["value"]
        });
      }
    })
});

export const WidgetConfigSchema = z.discriminatedUnion("kind", [
  TableWidgetConfigSchema,
  StatWidgetConfigSchema,
  ChartPlaceholderWidgetConfigSchema,
  FeedWidgetConfigSchema,
  DialPlaceholderWidgetConfigSchema
]);

export const WidgetCollectionSchema = z
  .object({
    version: z.number().int().min(1).default(1),
    widgets: z.array(WidgetConfigSchema).max(128)
  })
  .strict();

export type WidgetKind = z.infer<typeof WidgetKindSchema>;
export type WidgetConfig = z.infer<typeof WidgetConfigSchema>;
export type WidgetCollection = z.infer<typeof WidgetCollectionSchema>;
export type TableWidgetConfig = z.infer<typeof TableWidgetConfigSchema>;
export type StatWidgetConfig = z.infer<typeof StatWidgetConfigSchema>;
export type FeedWidgetConfig = z.infer<typeof FeedWidgetConfigSchema>;
export type ChartPlaceholderWidgetConfig = z.infer<typeof ChartPlaceholderWidgetConfigSchema>;
export type DialPlaceholderWidgetConfig = z.infer<typeof DialPlaceholderWidgetConfigSchema>;

export function isWidgetVisible(widget: WidgetConfig): boolean {
  return !widget.hidden;
}

export function getWidgetRefreshMs(widget: WidgetConfig): number | null {
  if (widget.refresh.mode !== "interval" || widget.refresh.intervalSeconds === null) {
    return null;
  }

  return widget.refresh.intervalSeconds * 1000;
}

export function sortWidgetsByPinAndTitle(widgets: readonly WidgetConfig[]): WidgetConfig[] {
  return [...widgets].sort((left, right) => {
    if (left.pinned !== right.pinned) {
      return left.pinned ? -1 : 1;
    }

    return left.title.localeCompare(right.title);
  });
}
