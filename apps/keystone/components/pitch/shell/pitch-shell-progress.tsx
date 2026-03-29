import Link from "next/link";
import { Badge, cn } from "@hitech/ui-kit";
import type { PitchDeckProgressModel } from "./types";

export interface PitchShellProgressProps {
  readonly model: PitchDeckProgressModel;
  readonly className?: string;
}

export function PitchShellProgress({ model, className }: PitchShellProgressProps) {
  const ratio = model.total > 0 ? Math.round((model.current / model.total) * 100) : 0;

  return (
    <div className={cn("pitch-glass-card pitch-neon-edge p-3", className)}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="grid gap-1">
          <p className="m-0 text-[0.7rem] uppercase tracking-[0.11em] text-[color:rgba(4,18,25,0.62)]">
            DECK PROGRESS
          </p>
          <p className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">{model.label}</p>
        </div>
        <Badge tone="accent">{ratio}%</Badge>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-[rgba(2,111,134,0.16)]">
        <span
          className="block h-full rounded-full bg-[linear-gradient(90deg,#AB7B26,#02A7CA)]"
          style={{ width: `${ratio}%` }}
        />
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {model.previousHref ? (
          <Link
            href={model.previousHref}
            className="pitch-focus-ring rounded-md border border-[rgba(2,111,134,0.25)] px-2 py-1 text-xs font-medium text-[color:var(--pitch-deep-teal)] no-underline hover:bg-[rgba(2,111,134,0.08)]"
          >
            Previous
          </Link>
        ) : null}
        {model.nextHref ? (
          <Link
            href={model.nextHref}
            className="pitch-focus-ring rounded-md border border-[rgba(2,111,134,0.25)] px-2 py-1 text-xs font-medium text-[color:var(--pitch-deep-teal)] no-underline hover:bg-[rgba(2,111,134,0.08)]"
          >
            Next
          </Link>
        ) : null}
      </div>
    </div>
  );
}
