import type { ReactNode } from "react";
import { Inbox, OctagonAlert, Sparkles, TriangleAlert } from "lucide-react";

import { toneFromSeverity } from "@/lib/ui/contracts";
import { cn } from "@/lib/utils";

const toneClass = {
  default: {
    shell: "border-white/10 bg-canvas/28",
    icon: "border-white/10 bg-white/6 text-accent",
    title: "text-text",
    copy: "text-muted"
  },
  warning: {
    shell: "border-warning/25 bg-warning/8",
    icon: "border-warning/25 bg-warning/10 text-warning",
    title: "text-warning",
    copy: "text-muted"
  },
  danger: {
    shell: "border-danger/25 bg-danger/8",
    icon: "border-danger/25 bg-danger/10 text-danger",
    title: "text-danger",
    copy: "text-muted"
  },
  success: {
    shell: "border-success/25 bg-success/8",
    icon: "border-success/25 bg-success/10 text-success",
    title: "text-success",
    copy: "text-muted"
  },
  accent: {
    shell: "border-accent/25 bg-accent/8",
    icon: "border-accent/25 bg-accent/10 text-accent",
    title: "text-accent",
    copy: "text-muted"
  }
} as const;

const defaultIcon = {
  default: <Inbox className="h-5 w-5" />,
  warning: <TriangleAlert className="h-5 w-5" />,
  danger: <OctagonAlert className="h-5 w-5" />,
  success: <Sparkles className="h-5 w-5" />,
  accent: <Sparkles className="h-5 w-5" />
} as const;

export interface EmptyStateProps {
  title: string;
  description?: string;
  eyebrow?: string;
  tone?: keyof typeof toneClass;
  icon?: ReactNode;
  action?: ReactNode;
  footer?: ReactNode;
  compact?: boolean;
  className?: string;
}

export function EmptyState({
  title,
  description,
  eyebrow,
  tone = "default",
  icon,
  action,
  footer,
  compact = false,
  className
}: EmptyStateProps) {
  const resolvedTone = toneFromSeverity(tone);
  const palette = toneClass[resolvedTone];

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-[1.75rem] border px-5 text-center shadow-glass backdrop-blur-xl",
        compact ? "py-8" : "py-12",
        palette.shell,
        className
      )}
    >
      <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />
      <div className={cn("mx-auto mb-4 inline-flex items-center justify-center rounded-2xl border", compact ? "h-12 w-12" : "h-14 w-14", palette.icon)}>
        {icon ?? defaultIcon[resolvedTone]}
      </div>
      {eyebrow ? <div className="mb-2 text-[11px] uppercase tracking-[0.22em] text-muted">{eyebrow}</div> : null}
      <h3 className={cn("text-balance font-semibold", compact ? "text-lg" : "text-xl", palette.title)}>{title}</h3>
      {description ? <p className={cn("mx-auto mt-2 max-w-2xl text-sm leading-6", palette.copy)}>{description}</p> : null}
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
      {footer ? <div className="mt-4 text-xs text-muted">{footer}</div> : null}
    </div>
  );
}
