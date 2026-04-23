import type { ReactNode } from "react";
import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";

import { toDisplayText, toneFromSeverity } from "@/lib/ui/contracts";
import { cn } from "@/lib/utils";

const toneClass = {
  default: "text-text",
  accent: "text-accent",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger"
} as const;

export interface StatCardProps {
  label: string;
  value: string | number;
  meta?: string;
  trendLabel?: string;
  trendDirection?: "up" | "flat" | "down";
  tone?: keyof typeof toneClass;
  icon?: ReactNode;
  emphasized?: boolean;
  className?: string;
}

export function StatCard({
  label,
  value,
  meta,
  trendLabel,
  trendDirection = "flat",
  tone = "default",
  icon,
  emphasized = false,
  className
}: StatCardProps) {
  const resolvedTone = toneFromSeverity(tone);
  const TrendIcon = trendDirection === "up" ? ArrowUpRight : trendDirection === "down" ? ArrowDownRight : ArrowRight;

  return (
    <div className={cn("surface-panel relative overflow-hidden p-3.5", emphasized && "surface-elevated", className)}>
      <div className="keyline pointer-events-none absolute inset-x-3.5 top-0" />
      <div className="flex items-start justify-between gap-2.5">
        <div>
          <div className="text-[10px] uppercase tracking-[0.14em] text-muted">{label}</div>
          <div className={cn("mt-1.5 text-[1.75rem] font-semibold tracking-[-0.03em]", toneClass[resolvedTone])}>{toDisplayText(value)}</div>
        </div>
        {icon ? <div className="surface-muted inline-flex h-9 w-9 items-center justify-center text-muted">{icon}</div> : null}
      </div>
      {(meta || trendLabel) ? (
        <div className="mt-3 flex flex-wrap items-center gap-2.5 text-xs">
          {trendLabel ? (
            <div className={cn("inline-flex items-center gap-1.5 rounded-full border px-2 py-1", resolvedTone === "default" ? "border-border/50 text-muted" : `border-current/20 ${toneClass[resolvedTone]}`)}>
              <TrendIcon className="h-3.5 w-3.5" />
              {trendLabel}
            </div>
          ) : null}
          {meta ? <div className="text-muted">{meta}</div> : null}
        </div>
      ) : null}
    </div>
  );
}
