import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface SectionHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  actions?: ReactNode;
  badge?: ReactNode;
  align?: "left" | "center";
  className?: string;
}

export function SectionHeader({
  title,
  description,
  eyebrow,
  actions,
  badge,
  align = "left",
  className
}: SectionHeaderProps) {
  const centered = align === "center";

  return (
    <div className={cn("flex gap-3", centered ? "flex-col items-center text-center" : "items-start justify-between", className)}>
      <div className={cn("min-w-0", centered ? "max-w-3xl" : "max-w-2xl")}>
        {eyebrow ? <div className="mb-1 text-[11px] uppercase tracking-[0.22em] text-accent/80">{eyebrow}</div> : null}
        <div className={cn("flex gap-2", centered ? "flex-col items-center" : "items-center")}>
          <h2 className="text-lg font-semibold tracking-[-0.01em] text-text">{title}</h2>
          {badge ? <div className="shrink-0">{badge}</div> : null}
        </div>
        {description ? <p className="mt-1 text-sm leading-6 text-muted">{description}</p> : null}
      </div>
      {actions ? <div className={cn("flex shrink-0 flex-wrap gap-2", centered ? "justify-center" : "justify-end")}>{actions}</div> : null}
    </div>
  );
}
