import { Badge, cn } from "@hitech/ui-kit";
import type { PitchNavModel } from "./types";

export interface PitchNavProps {
  readonly model: PitchNavModel;
  readonly className?: string;
}

export function PitchNav({ model, className }: PitchNavProps) {
  return (
    <nav
      className={cn("grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6", className)}
      aria-label="Pitch navigation"
    >
      <div className="pitch-rail-static-card inline-flex h-9 items-center justify-between gap-3 rounded-[var(--ui-core-radius-sm)] border px-3 text-sm font-medium">
        <span className="truncate text-left">Mission Control</span>
        <span className="text-xs text-[hsl(var(--ui-text-3))]">Home</span>
      </div>
      {model.links.map((link) => {
        const isActive = link.slug === model.activeSlug;
        return (
          <article
            key={link.slug}
            className={cn(
              "pitch-rail-static-card inline-flex h-9 items-center justify-between gap-3 rounded-[var(--ui-core-radius-sm)] border px-3 text-sm font-medium",
              isActive
                ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent-soft))] text-[hsl(var(--ui-accent))]"
                : "border-[hsl(var(--ui-border-2))] bg-[hsl(var(--ui-surface-1))] text-[hsl(var(--ui-text-2))]"
            )}
          >
            <span className="truncate text-left">{link.title}</span>
            {isActive ? (
              <Badge tone="accent">Actual</Badge>
            ) : (
              <span className="text-xs text-[hsl(var(--ui-text-3))]">{link.order}</span>
            )}
          </article>
        );
      })}
    </nav>
  );
}
