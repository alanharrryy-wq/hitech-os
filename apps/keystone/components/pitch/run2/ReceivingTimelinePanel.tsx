"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip } from "./primitives";
import { getReceivingStateTone } from "./store";

export interface ReceivingTimelinePanelProps {
  readonly context: ImportReceivingPanelContext;
}

export function ReceivingTimelinePanel({ context }: ReceivingTimelinePanelProps) {
  const { state } = context;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Transition timeline"
        description="Deterministic transition log for ARRIVED -> DOCS_HOLD -> RECEIVED -> QUARANTINE"
      >
        <ScrollArea className="h-[320px] pr-2">
          <ol className="m-0 grid list-none gap-2 p-0">
            {state.timeline
              .slice()
              .reverse()
              .map((entry) => (
                <li
                  key={entry.id}
                  className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.9)] p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Chip tone="neutral">#{entry.sequence}</Chip>
                      <Chip tone="accent">{entry.action}</Chip>
                    </div>
                    <Chip tone={getReceivingStateTone(entry.to)}>
                      {entry.from} {"->"} {entry.to}
                    </Chip>
                  </div>
                  <p className="m-0 mt-1 text-xs font-semibold text-[hsl(var(--ui-text-1))]">
                    {entry.note}
                  </p>
                  {entry.reasons.length > 0 ? (
                    <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-[11px] text-[hsl(var(--ui-text-2))]">
                      {entry.reasons.map((reason) => (
                        <li key={reason}>{reason}</li>
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
