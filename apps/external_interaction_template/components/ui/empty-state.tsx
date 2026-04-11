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
        "relative overflow-hidden rounded-[1.55rem] border px-4 sm:px-5 text-center shadow-glass backdrop-blur-lg",
        compact ? "py-7" : "py-10",
        palette.shell,
        className
      )}
    >
      <div className="pointer-events-none absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-white/12 to-transparent" />
      <div className={cn("mx-auto mb-4 inline-flex items-center justify-center rounded-2xl border", compact ? "h-11 w-11" : "h-13 w-13", palette.icon)}>
        {icon ?? defaultIcon[resolvedTone]}
      </div>
      {eyebrow ? <div className="mb-1.5 text-[10px] uppercase tracking-[0.2em] text-muted">{eyebrow}</div> : null}
      <h3 className={cn("text-balance font-semibold", compact ? "text-lg" : "text-xl", palette.title)}>{title}</h3>
      {description ? <p className={cn("mx-auto mt-1.5 max-w-2xl text-sm leading-5", palette.copy)}>{description}</p> : null}
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
      {footer ? <div className="mt-3 text-xs text-muted">{footer}</div> : null}
    </div>
  );
}
