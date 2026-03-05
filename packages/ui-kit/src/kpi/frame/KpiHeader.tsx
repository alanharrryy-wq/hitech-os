"use client";

import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type { KpiStyleId, KpiSurfaceId, PerfProfile, SemanticIntent } from "../types.js";

export interface KpiHeaderProps extends HTMLAttributes<HTMLDivElement> {
  readonly title: string;
  readonly subtitle?: string | undefined;
  readonly value?: string | number | undefined;
  readonly unit?: string | undefined;
  readonly styleId?: KpiStyleId | undefined;
  readonly surface?: KpiSurfaceId | undefined;
  readonly intent?: SemanticIntent | undefined;
  readonly perfProfile?: PerfProfile | undefined;
}

export function KpiHeader({
  title,
  subtitle,
  value,
  unit,
  styleId,
  surface,
  intent,
  perfProfile,
  className,
  ...props
}: KpiHeaderProps) {
  const theme = useKpiTheme({ styleId, surface, intent, perfProfile });

  return (
    <header className={cn("kpi-header grid gap-2", className)} {...props}>
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p
            className="m-0 text-[0.66rem]"
            style={{
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              fontVariantCaps: "all-small-caps",
              color: theme.text.muted
            }}
          >
            {title}
          </p>
          {subtitle ? (
            <p className="m-0 mt-1 text-xs" style={{ color: theme.text.secondary }}>
              {subtitle}
            </p>
          ) : null}
        </div>

        {value !== undefined ? (
          <p
            className="m-0 whitespace-nowrap text-right text-xl font-semibold"
            style={{
              color: theme.text.primary,
              fontVariantNumeric: "tabular-nums lining-nums",
              lineHeight: 1.05
            }}
          >
            <span>{value}</span>
            {unit ? (
              <span
                className="ml-1 align-baseline text-[0.78rem] font-medium"
                style={{ color: theme.text.secondary }}
              >
                {unit}
              </span>
            ) : null}
          </p>
        ) : null}
      </div>
    </header>
  );
}
