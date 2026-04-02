import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function Surface({
  children,
  className,
  title,
  subtitle,
  actions
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <section className={cn("rounded-2xl border border-white/10 bg-surface/58 p-4 backdrop-blur-xl shadow-glass", className)}>
      {(title || subtitle || actions) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-base font-semibold text-text">{title}</h2>}
            {subtitle && <p className="mt-1 text-xs text-muted">{subtitle}</p>}
          </div>
          {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
        </header>
      )}
      {children}
    </section>
  );
}
