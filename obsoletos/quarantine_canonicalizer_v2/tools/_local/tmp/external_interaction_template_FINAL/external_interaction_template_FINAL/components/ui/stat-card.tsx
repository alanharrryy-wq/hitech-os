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
    <div className={cn("relative overflow-hidden rounded-2xl border border-white/10 bg-canvas/32 p-4 shadow-[0_12px_40px_rgba(0,0,0,0.18)]", emphasized && "bg-surface/70 shadow-glass", className)}>
      <div className="pointer-events-none absolute inset-x-4 top-0 h-px bg-gradient-to-r from-transparent via-white/14 to-transparent" />
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[11px] uppercase tracking-[0.16em] text-muted">{label}</div>
          <div className={cn("mt-2 text-3xl font-semibold tracking-[-0.03em]", toneClass[resolvedTone])}>{toDisplayText(value)}</div>
        </div>
        {icon ? <div className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/6 text-muted">{icon}</div> : null}
      </div>
      {(meta || trendLabel) ? (
        <div className="mt-4 flex flex-wrap items-center gap-3 text-xs">
          {trendLabel ? (
            <div className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1", resolvedTone === "default" ? "border-white/10 text-muted" : `border-current/20 ${toneClass[resolvedTone]}`)}>
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
