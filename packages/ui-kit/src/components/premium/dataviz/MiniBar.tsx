import type { HTMLAttributes } from "react";
import { cn } from "../../../lib/cn.js";

export interface MiniBarItem {
  readonly id: string;
  readonly value: number;
  readonly label?: string;
}

export interface MiniBarProps extends HTMLAttributes<HTMLDivElement> {
  readonly items: readonly MiniBarItem[];
  readonly max?: number;
}

export function MiniBar({ items, max, className, ...props }: MiniBarProps) {
  const computedMax = max ?? Math.max(1, ...items.map((item) => item.value));

  return (
    <div className={cn("ui-viz-minibar grid grid-cols-1 gap-1.5", className)} {...props}>
      {items.map((item, index) => {
        const width = Math.max(0, Math.min(100, (item.value / computedMax) * 100));
        const gradientClass = `ui-premium-gradient-${String((index % 120) + 1).padStart(3, "0")}`;
        return (
          <div key={item.id} className="grid gap-1">
            {item.label ? (
              <div className="flex items-center justify-between gap-2 text-[11px] text-[hsl(var(--ui-text-3))]">
                <span className="truncate">{item.label}</span>
                <span>{item.value}</span>
              </div>
            ) : null}
            <div className="h-2 overflow-hidden rounded-full bg-[rgba(17,21,26,0.1)]">
              <div
                className={cn("h-full rounded-full", gradientClass)}
                style={{ width: `${width}%` }}
                role="img"
                aria-label={item.label ? `${item.label} ${item.value}` : `Value ${item.value}`}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
