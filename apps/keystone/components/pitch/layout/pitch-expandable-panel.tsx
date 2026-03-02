"use client";

import { useId, useState } from "react";
import { cn } from "@hitech/ui-kit";

export interface PitchExpandablePanelProps {
  readonly title: string;
  readonly subtitle?: string;
  readonly defaultOpen?: boolean;
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function PitchExpandablePanel({
  title,
  subtitle,
  defaultOpen = false,
  className,
  children
}: PitchExpandablePanelProps) {
  const [open, setOpen] = useState(defaultOpen);
  const contentId = useId();

  return (
    <section
      className={cn(
        "pitch-collapsible-panel pitch-glass-card pitch-neon-edge overflow-hidden",
        className
      )}
      aria-expanded={open}
    >
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-controls={contentId}
        aria-expanded={open}
        className="pitch-focus-ring flex w-full items-center justify-between gap-3 px-4 py-3 text-left"
      >
        <span className="grid gap-1">
          <span className="text-sm font-semibold text-[color:var(--pitch-ink)]">{title}</span>
          {subtitle ? (
            <span className="text-xs text-[color:rgba(4,18,25,0.66)]">{subtitle}</span>
          ) : null}
        </span>
        <span className="text-xs font-semibold text-[color:#026F86]">{open ? "Collapse" : "Expand"}</span>
      </button>

      {open ? (
        <div id={contentId} className="border-t border-[rgba(2,111,134,0.16)] px-4 py-3">
          {children}
        </div>
      ) : null}
    </section>
  );
}
