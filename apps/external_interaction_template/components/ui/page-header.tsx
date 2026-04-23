import type { ReactNode } from "react";

import { runtimeShellClass, type RuntimeUiContext } from "@/lib/ui/runtime";
import { cn } from "@/lib/utils";

export interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  kicker?: ReactNode;
  actions?: ReactNode;
  stats?: ReactNode;
  children?: ReactNode;
  align?: "left" | "center";
  compact?: boolean;
  runtime?: RuntimeUiContext;
  className?: string;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  kicker,
  actions,
  stats,
  children,
  align = "left",
  compact = false,
  runtime,
  className
}: PageHeaderProps) {
  const centered = align === "center";

  return (
    <header
      className={cn(
        "surface-shell relative overflow-hidden px-3.5 sm:px-4",
        compact ? "py-3.5" : "py-4",
        runtime ? runtimeShellClass(runtime) : undefined,
        className
      )}
    >
      <div className="keyline pointer-events-none absolute inset-x-5 top-0" />
      <div className={cn("flex gap-3", centered ? "flex-col items-center text-center" : "flex-col lg:flex-row lg:items-start lg:justify-between")}>
        <div className={cn("min-w-0", centered ? "max-w-3xl" : "max-w-4xl")}>
          {eyebrow ? <div className="mb-1 text-[10px] uppercase tracking-[0.18em] text-accent/80">{eyebrow}</div> : null}
          <div className={cn("flex gap-3", centered ? "flex-col items-center" : "items-start justify-between")}>
            <div className="min-w-0">
              <h1 className={cn("text-balance font-semibold tracking-[-0.02em] text-text", compact ? "text-[1.44rem]" : "text-[1.7rem] sm:text-[1.8rem]")}>{title}</h1>
              {description ? <p className="mt-1 max-w-3xl text-sm leading-5 text-muted">{description}</p> : null}
            </div>
            {kicker ? <div className="shrink-0">{kicker}</div> : null}
          </div>
          {children ? <div className="mt-2.5">{children}</div> : null}
        </div>
        {actions ? <div className={cn("flex shrink-0 flex-wrap gap-1.5", centered ? "justify-center" : "lg:justify-end")}>{actions}</div> : null}
      </div>
      {stats ? <div className={cn("mt-3", centered ? "flex justify-center" : "")}>{stats}</div> : null}
    </header>
  );
}
