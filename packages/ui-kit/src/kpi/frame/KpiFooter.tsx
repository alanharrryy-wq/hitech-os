"use client";

import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { useKpiTheme } from "../theme/useKpiTheme.js";
import type { KpiStyleId, KpiSurfaceId, PerfProfile, SemanticIntent } from "../types.js";

export interface KpiFooterProps extends HTMLAttributes<HTMLDivElement> {
  readonly note?: string | undefined;
  readonly change?: string | undefined;
  readonly styleId?: KpiStyleId | undefined;
  readonly surface?: KpiSurfaceId | undefined;
  readonly intent?: SemanticIntent | undefined;
  readonly perfProfile?: PerfProfile | undefined;
  readonly className?: string;
}

export function KpiFooter({
  note,
  change,
  styleId,
  surface,
  intent,
  perfProfile,
  className,
  ...props
}: KpiFooterProps) {
  if (!note && !change) {
    return null;
  }

  const theme = useKpiTheme({ styleId, surface, intent, perfProfile });

  return (
    <footer
      className={cn("kpi-footer mt-3 flex items-center justify-between gap-2 border-t pt-2", className)}
      style={{ borderTopColor: theme.frame.hairline }}
      {...props}
    >
      <p className="m-0 text-xs" style={{ color: theme.text.muted }}>
        {note ?? ""}
      </p>
      {change ? (
        <p
          className="m-0 text-xs font-medium"
          style={{ color: theme.text.secondary, fontVariantNumeric: "tabular-nums" }}
        >
          {change}
        </p>
      ) : null}
    </footer>
  );
}
