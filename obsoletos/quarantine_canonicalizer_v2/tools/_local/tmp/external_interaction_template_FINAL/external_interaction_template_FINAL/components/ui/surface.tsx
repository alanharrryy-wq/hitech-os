import type { ReactNode } from "react";

import { SectionHeader } from "@components/ui/section-header";
import { cn } from "@/lib/utils";

const variantClass = {
  base: "surface-muted",
  panel: "surface-panel",
  elevated: "surface-elevated",
  shell: "surface-shell"
} as const;

const paddingClass = {
  sm: "p-4",
  md: "p-5 sm:p-6",
  lg: "p-6 sm:p-7"
} as const;

export function Surface({
  children,
  className,
  title,
  subtitle,
  actions,
  eyebrow,
  variant = "panel",
  padding = "md"
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  eyebrow?: string;
  variant?: keyof typeof variantClass;
  padding?: keyof typeof paddingClass;
}) {
  return (
    <section className={cn(variantClass[variant], paddingClass[padding], className)}>
      {title ? <SectionHeader className="mb-5" eyebrow={eyebrow} title={title} description={subtitle} actions={actions} /> : null}
      {!title && (subtitle || actions || eyebrow) ? (
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            {eyebrow ? <div className="mb-1 text-[11px] uppercase tracking-[0.22em] text-accent/80">{eyebrow}</div> : null}
            {subtitle ? <p className="text-sm leading-6 text-muted">{subtitle}</p> : null}
          </div>
          {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}
