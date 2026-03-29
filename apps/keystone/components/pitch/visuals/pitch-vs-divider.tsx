"use client";

import { useState } from "react";
import { cn } from "@hitech/ui-kit";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";

export interface PitchVsDividerProps {
  readonly title?: string;
  readonly summary: string;
  readonly details: readonly string[];
  readonly className?: string;
}

export function PitchVsDivider({
  title = "VS",
  summary,
  details,
  className
}: PitchVsDividerProps) {
  const [active, setActive] = useState(false);

  return (
    <div
      className={cn("grid gap-2", className)}
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
    >
      <button
        type="button"
        onClick={() => setActive((value) => !value)}
        className={cn(
          "pitch-focus-ring pitch-glass-card pitch-neon-edge inline-flex h-12 items-center justify-center rounded-full px-4 text-sm font-semibold",
          active ? "pitch-halo-level-180" : "pitch-halo-level-60"
        )}
        aria-pressed={active}
      >
        {title}
      </button>

      <PitchExpandablePanel
        title={summary}
        subtitle="Comparative detail"
        defaultOpen={active}
      >
        <ul className="m-0 list-disc space-y-1 pl-5 text-sm text-[color:rgba(4,18,25,0.78)]">
          {details.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </PitchExpandablePanel>
    </div>
  );
}
