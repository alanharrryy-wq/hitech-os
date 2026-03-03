"use client";

import { useMemo } from "react";
import { ScrollArea, ScrollBar, cn } from "@hitech/ui-kit";
import type { PitchDeckProgressModel, PitchShellNavModel } from "../shell/types";
import { PitchRailNavItem } from "./pitch-rail-nav-item";

export interface PitchRailNavProps {
  readonly model: PitchShellNavModel;
  readonly progress: PitchDeckProgressModel;
  readonly className?: string;
}

export function PitchRailNav({ model, progress, className }: PitchRailNavProps) {
  const activeOrder = useMemo(() => {
    const active = model.links.find((link) => link.slug === model.activeSlug);
    return active?.order ?? progress.current;
  }, [model.activeSlug, model.links, progress.current]);

  return (
    <nav className={cn("pitch-glass-card pitch-neon-edge p-3", className)} aria-label="Pitch screen rail navigation">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="pitch-rail-static-card rounded-full border px-3 py-1 text-xs font-semibold text-[color:var(--pitch-ink)]">
            Mission Control
          </span>
          <span className="pitch-rail-static-card rounded-full border px-3 py-1 text-xs font-semibold text-[color:var(--pitch-ink)]">
            Pitch Index
          </span>
        </div>
        <p className="m-0 text-xs text-[color:rgba(4,18,25,0.62)]">Navigate with Deck Progress controls.</p>
      </div>

      <ScrollArea className="w-full whitespace-nowrap">
        <div className="inline-flex gap-3 pb-2">
          {model.links.map((link) => (
            <PitchRailNavItem
              key={link.slug}
              link={link}
              {...(model.activeSlug ? { activeSlug: model.activeSlug } : {})}
              progressCurrent={activeOrder}
            />
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </nav>
  );
}
