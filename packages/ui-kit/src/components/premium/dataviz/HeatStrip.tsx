import type { HTMLAttributes } from "react";
import { cn } from "../../../lib/cn.js";

export interface HeatStripProps extends HTMLAttributes<HTMLDivElement> {
  readonly values: readonly number[];
  readonly min?: number;
  readonly max?: number;
}

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

export function HeatStrip({ values, min, max, className, ...props }: HeatStripProps) {
  const computedMin = min ?? Math.min(...values, 0);
  const computedMax = max ?? Math.max(...values, 1);
  const span = Math.max(1, computedMax - computedMin);

  return (
    <div className={cn("ui-viz-heatstrip grid grid-flow-col gap-1", className)} {...props}>
      {values.map((entry, index) => {
        const ratio = clamp01((entry - computedMin) / span);
        const opacity = 0.12 + ratio * 0.82;
        return (
          <span
            key={`${index}-${entry}`}
            className="h-4 w-2 rounded-sm"
            style={{
              background: `linear-gradient(180deg, rgba(2, 167, 202, ${opacity.toFixed(3)}) 0%, rgba(171, 123, 38, ${(opacity * 0.65).toFixed(3)}) 100%)`
            }}
            role="img"
            aria-label={`Heat ${entry}`}
          />
        );
      })}
    </div>
  );
}
