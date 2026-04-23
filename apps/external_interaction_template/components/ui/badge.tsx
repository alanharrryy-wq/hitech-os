import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

const toneClass = {
  default: "ui-badge-default",
  success: "ui-badge-success",
  warning: "ui-badge-warning",
  danger: "ui-badge-danger",
  accent: "ui-badge-accent"
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
        "ui-badge",
        toneClass[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
