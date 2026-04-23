import type { ReactNode } from "react";
import { AlertTriangle, CircleDashed, OctagonAlert, Sparkles } from "lucide-react";

import { toneFromSeverity } from "@/lib/ui/contracts";
import { cn } from "@/lib/utils";

const toneClass = {
  default: {
    shell: "surface-panel",
    halo: "from-accent/14 via-accent/4 to-transparent",
    icon: "surface-muted text-accent",
    eyebrow: "text-accent/85",
    title: "text-text"
  },
  warning: {
    shell: "surface-panel border-warning/30 bg-warning/8",
    halo: "from-warning/16 via-warning/4 to-transparent",
    icon: "surface-muted border-warning/30 bg-warning/12 text-warning",
    eyebrow: "text-warning",
    title: "text-warning"
  },
  danger: {
    shell: "surface-panel border-danger/30 bg-danger/8",
    halo: "from-danger/16 via-danger/4 to-transparent",
    icon: "surface-muted border-danger/30 bg-danger/12 text-danger",
    eyebrow: "text-danger",
    title: "text-danger"
  },
  success: {
    shell: "surface-panel border-success/30 bg-success/8",
    halo: "from-success/16 via-success/4 to-transparent",
    icon: "surface-muted border-success/30 bg-success/12 text-success",
    eyebrow: "text-success",
    title: "text-success"
  },
  accent: {
    shell: "surface-panel border-accent/30 bg-accent/8",
    halo: "from-accent/16 via-accent/4 to-transparent",
    icon: "surface-muted border-accent/30 bg-accent/12 text-accent",
    eyebrow: "text-accent",
    title: "text-accent"
  }
} as const;

const defaultIcon = {
  default: <CircleDashed className="h-5 w-5" />,
  warning: <AlertTriangle className="h-5 w-5" />,
  danger: <OctagonAlert className="h-5 w-5" />,
  success: <Sparkles className="h-5 w-5" />,
  accent: <Sparkles className="h-5 w-5" />
} as const;

export interface StatusPanelProps {
  title: string;
  description?: string;
  eyebrow?: string;
  tone?: keyof typeof toneClass;
  icon?: ReactNode;
  actions?: ReactNode;
  meta?: ReactNode;
  children?: ReactNode;
  size?: "md" | "lg";
  className?: string;
}

export function StatusPanel({
  title,
  description,
  eyebrow,
  tone = "default",
  icon,
  actions,
  meta,
  children,
  size = "md",
  className
}: StatusPanelProps) {
  const resolvedTone = toneFromSeverity(tone);
  const palette = toneClass[resolvedTone];

  return (
    <section className={cn("relative isolate overflow-hidden px-4 sm:px-5", size === "lg" ? "max-w-2xl py-7" : "py-5", palette.shell, className)}>
      <div className={cn("pointer-events-none absolute inset-0 bg-gradient-to-br opacity-90", palette.halo)} />
      <div className="keyline pointer-events-none absolute inset-x-5 top-0" />
      <div className="relative z-10">
        <div className="flex items-start gap-4">
          <div className={cn("inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-[1rem]", palette.icon)}>
            {icon ?? defaultIcon[resolvedTone]}
          </div>
          <div className="min-w-0 flex-1">
            {eyebrow ? <div className={cn("mb-1 text-[11px] uppercase tracking-[0.22em]", palette.eyebrow)}>{eyebrow}</div> : null}
            <h2 className={cn("text-balance font-semibold tracking-[-0.02em]", size === "lg" ? "text-[1.6rem]" : "text-[1.15rem]", palette.title)}>{title}</h2>
            {description ? <p className="mt-1.5 max-w-2xl text-sm leading-5 text-muted">{description}</p> : null}
            {children ? <div className="mt-3">{children}</div> : null}
            {(actions || meta) ? (
              <div className="mt-4 flex flex-wrap items-center gap-2.5">
                {actions}
                {meta ? <div className="text-xs text-muted">{meta}</div> : null}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  );
}
