import { z } from "zod";
import { WidgetIdSchema } from "../brands.js";

export const DashboardBreakpointSchema = z.enum(["xs", "sm", "md", "lg", "xl", "xxl"]);

export const PanelSizeSchema = z.enum(["xs", "sm", "md", "lg", "xl"]);

export const GridPositionSchema = z
  .object({
    x: z.number().int().min(0),
    y: z.number().int().min(0),
    w: z.number().int().min(1),
    h: z.number().int().min(1),
    minW: z.number().int().min(1).max(24).default(1),
    minH: z.number().int().min(1).max(24).default(1),
    maxW: z.number().int().min(1).max(24).nullable().default(null),
    maxH: z.number().int().min(1).max(24).nullable().default(null)
  })
  .strict()
  .superRefine((value, ctx) => {
    if (value.w < value.minW) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["w"],
        message: "w must be >= minW"
      });
    }

    if (value.h < value.minH) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["h"],
        message: "h must be >= minH"
      });
    }

    if (value.maxW !== null && value.w > value.maxW) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["w"],
        message: "w must be <= maxW"
      });
    }

    if (value.maxH !== null && value.h > value.maxH) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["h"],
        message: "h must be <= maxH"
      });
    }
  });

export const GridLayoutItemSchema = z
  .object({
    widgetId: WidgetIdSchema,
    position: GridPositionSchema,
    locked: z.boolean().default(false),
    resizable: z.boolean().default(true),
    draggable: z.boolean().default(true),
    panelSize: PanelSizeSchema.default("md")
  })
  .strict();

export const BreakpointGridLayoutSchema = z
  .object({
    breakpoint: DashboardBreakpointSchema,
    columns: z.number().int().min(1).max(24),
    rowHeight: z.number().int().min(40).max(480),
    gap: z.number().int().min(0).max(64),
    items: z.array(GridLayoutItemSchema).max(240)
  })
  .strict();

export const GridLayoutConfigSchema = z
  .object({
    version: z.number().int().min(1),
    breakpoints: z.array(BreakpointGridLayoutSchema).min(1),
    compactType: z.enum(["vertical", "horizontal", "none"]).default("vertical"),
    bounded: z.boolean().default(true),
    allowOverlap: z.boolean().default(false)
  })
  .strict()
  .superRefine((value, ctx) => {
    const names = new Set<string>();
    for (const bp of value.breakpoints) {
      if (names.has(bp.breakpoint)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["breakpoints"],
          message: `Duplicate breakpoint: ${bp.breakpoint}`
        });
      }
      names.add(bp.breakpoint);

      const collision = findFirstCollision(bp.items, bp.columns);
      if (collision !== null && !value.allowOverlap) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["breakpoints"],
          message: `Collision between ${collision.a} and ${collision.b} at ${bp.breakpoint}`
        });
      }
    }
  });

export type DashboardBreakpoint = z.infer<typeof DashboardBreakpointSchema>;
export type PanelSize = z.infer<typeof PanelSizeSchema>;
export type GridPosition = z.infer<typeof GridPositionSchema>;
export type GridLayoutItem = z.infer<typeof GridLayoutItemSchema>;
export type BreakpointGridLayout = z.infer<typeof BreakpointGridLayoutSchema>;
export type GridLayoutConfig = z.infer<typeof GridLayoutConfigSchema>;

function boxesOverlap(a: GridPosition, b: GridPosition): boolean {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function findFirstCollision(
  items: readonly GridLayoutItem[],
  columns: number
): { readonly a: string; readonly b: string } | null {
  for (const item of items) {
    const rightEdge = item.position.x + item.position.w;
    if (rightEdge > columns) {
      return {
        a: item.widgetId,
        b: `columns:${columns}`
      };
    }
  }

  for (let i = 0; i < items.length; i += 1) {
    for (let j = i + 1; j < items.length; j += 1) {
      const left = items[i];
      const right = items[j];
      if (left && right && boxesOverlap(left.position, right.position)) {
        return {
          a: left.widgetId,
          b: right.widgetId
        };
      }
    }
  }

  return null;
}

export function validateGridLayout(config: GridLayoutConfig): {
  readonly valid: boolean;
  readonly reason: string | null;
} {
  for (const breakpoint of config.breakpoints) {
    const collision = findFirstCollision(breakpoint.items, breakpoint.columns);
    if (collision !== null && !config.allowOverlap) {
      return {
        valid: false,
        reason: `Collision between ${collision.a} and ${collision.b} on ${breakpoint.breakpoint}`
      };
    }
  }

  return {
    valid: true,
    reason: null
  };
}

export function getBreakpointLayout(
  config: GridLayoutConfig,
  breakpoint: DashboardBreakpoint
): BreakpointGridLayout | undefined {
  return config.breakpoints.find((item) => item.breakpoint === breakpoint);
}
