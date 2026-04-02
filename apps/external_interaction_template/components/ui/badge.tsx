import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

const toneClass = {
  default: "bg-white/10 text-text border border-white/15",
  success: "bg-success/20 text-success border border-success/30",
  warning: "bg-warning/20 text-warning border border-warning/30",
  danger: "bg-danger/20 text-danger border border-danger/30",
  accent: "bg-accent/20 text-accent border border-accent/30"
} as const;

export function Badge({
  children,
  tone = "default",
  className
}: {
  children: ReactNode;
  tone?: keyof typeof toneClass;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex h-6 items-center rounded-full px-2.5 text-[11px] font-semibold uppercase tracking-[0.08em]",
        toneClass[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
