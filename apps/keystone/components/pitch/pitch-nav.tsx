import Link from "next/link";
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
      <Link
        href="/"
        className="inline-flex h-9 items-center justify-between gap-3 rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-2))] bg-[hsl(var(--ui-surface-1))] px-3 text-sm font-medium text-[hsl(var(--ui-text-2))] transition-colors hover:bg-[hsl(var(--ui-surface-2))]"
      >
        <span className="truncate text-left">Mission Control</span>
        <span className="text-xs text-[hsl(var(--ui-text-3))]">Home</span>
      </Link>
      {model.links.map((link) => {
        const isActive = link.slug === model.activeSlug;
        return (
          <Link
            key={link.slug}
            href={link.href}
            className={cn(
              "inline-flex h-9 items-center justify-between gap-3 rounded-[var(--ui-core-radius-sm)] border px-3 text-sm font-medium transition-colors",
              isActive
                ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent-soft))] text-[hsl(var(--ui-accent))]"
                : "border-[hsl(var(--ui-border-2))] bg-[hsl(var(--ui-surface-1))] text-[hsl(var(--ui-text-2))] hover:bg-[hsl(var(--ui-surface-2))]"
            )}
          >
            <span className="truncate text-left">{link.title}</span>
            {isActive ? (
              <Badge tone="accent">Actual</Badge>
            ) : (
              <span className="text-xs text-[hsl(var(--ui-text-3))]">{link.order}</span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
