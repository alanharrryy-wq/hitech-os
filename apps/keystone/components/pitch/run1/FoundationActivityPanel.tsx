"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext } from "./types";
import { Chip } from "./primitives";

export interface FoundationActivityPanelProps {
  readonly context: InventoryFoundationPanelContext;
}

export function FoundationActivityPanel({ context }: FoundationActivityPanelProps) {
  const { state } = context;

  return (
    <GlassCard className="p-4" tone="muted" backdrop="medium">
      <InsetPanel
        title="Control-Room Timeline"
        description="Deterministic event stream from inputs, docs and gating recomputes"
      >
        <ScrollArea className="h-[300px] pr-2">
          <ol className="m-0 grid list-none gap-2 p-0">
            {state.timeline
              .slice()
              .reverse()
              .map((entry) => (
                <li
                  key={entry.id}
                  className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.86)] p-2.5"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Chip tone="accent">{entry.kind}</Chip>
                      <Chip tone="neutral">{entry.actorRole.toUpperCase()}</Chip>
                    </div>
                    <p className="m-0 text-[11px] text-[hsl(var(--ui-text-3))]">{entry.at}</p>
                  </div>
                  <p className="m-0 mt-1 text-xs font-semibold text-[hsl(var(--ui-text-1))]">
                    {entry.message}
                  </p>
                  {entry.details.length > 0 ? (
                    <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-[11px] text-[hsl(var(--ui-text-2))]">
                      {entry.details.map((detail) => (
                        <li key={detail}>{detail}</li>
                      ))}
                    </ul>
                  ) : null}
                </li>
              ))}
          </ol>
        </ScrollArea>
      </InsetPanel>
    </GlassCard>
  );
}
