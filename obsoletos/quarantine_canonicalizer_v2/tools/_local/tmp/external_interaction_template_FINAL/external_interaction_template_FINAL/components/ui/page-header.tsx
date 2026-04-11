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
        "relative overflow-hidden rounded-[1.9rem] border border-white/10 px-5 backdrop-blur-xl",
        compact ? "py-5" : "py-6",
        runtime ? runtimeShellClass(runtime) : "bg-surface/58 shadow-glass",
        className
      )}
    >
      <div className="pointer-events-none absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-white/18 to-transparent" />
      <div className={cn("flex gap-4", centered ? "flex-col items-center text-center" : "flex-col lg:flex-row lg:items-start lg:justify-between")}>
        <div className={cn("min-w-0", centered ? "max-w-3xl" : "max-w-4xl")}>
          {eyebrow ? <div className="mb-2 text-[11px] uppercase tracking-[0.24em] text-accent/80">{eyebrow}</div> : null}
          <div className={cn("flex gap-3", centered ? "flex-col items-center" : "items-start justify-between")}>
            <div className="min-w-0">
              <h1 className={cn("text-balance font-semibold tracking-[-0.02em] text-text", compact ? "text-2xl" : "text-3xl sm:text-[2.15rem]")}>{title}</h1>
              {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{description}</p> : null}
            </div>
            {kicker ? <div className="shrink-0">{kicker}</div> : null}
          </div>
          {children ? <div className="mt-4">{children}</div> : null}
        </div>
        {actions ? <div className={cn("flex shrink-0 flex-wrap gap-2", centered ? "justify-center" : "lg:justify-end")}>{actions}</div> : null}
      </div>
      {stats ? <div className={cn("mt-5", centered ? "flex justify-center" : "")}>{stats}</div> : null}
    </header>
  );
}
