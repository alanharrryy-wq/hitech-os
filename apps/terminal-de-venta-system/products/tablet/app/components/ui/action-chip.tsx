import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function ActionChip({
  title,
  description,
  meta,
  tone = "ok",
  children,
}: {
  title: string;
  description: string;
  meta?: string;
  tone?: "ok" | "warn" | "danger";
  children?: ReactNode;
}) {
  return (
    <div className={cn("action-chip", `tone-${tone}`)}>
      <div className="action-chip-head">
        <strong>{title}</strong>
        {meta ? <span className="action-chip-meta">{meta}</span> : null}
      </div>
      <div className="subtle">{description}</div>
      {children ? <div className="action-chip-tail">{children}</div> : null}
    </div>
  );
}
