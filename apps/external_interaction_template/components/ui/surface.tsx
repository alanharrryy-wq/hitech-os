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
  sm: "p-3.5",
  md: "p-4 sm:p-5",
  lg: "p-5 sm:p-6"
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
      {title ? <SectionHeader className="mb-4" eyebrow={eyebrow} title={title} description={subtitle} actions={actions} /> : null}
      {!title && (subtitle || actions || eyebrow) ? (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="min-w-0">
            {eyebrow ? <div className="mb-0.5 text-[10px] uppercase tracking-[0.2em] text-accent/80">{eyebrow}</div> : null}
            {subtitle ? <p className="text-sm leading-5 text-muted">{subtitle}</p> : null}
          </div>
          {actions ? <div className="flex shrink-0 flex-wrap gap-1.5">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}
