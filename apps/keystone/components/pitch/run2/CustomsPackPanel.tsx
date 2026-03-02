"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip } from "./primitives";
import { getCustomsStatusTone } from "./store";

export interface CustomsPackPanelProps {
  readonly context: ImportReceivingPanelContext;
}

export function CustomsPackPanel({ context }: CustomsPackPanelProps) {
  const { state, computed, actions } = context;
  const criticalMissing = state.customsPack.filter(
    (document) => document.critical && document.status !== "present"
  );

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Customs Pack Panel"
        description="Checklist status + gate blockers for receiving progression"
      >
        <div className="flex flex-wrap items-center gap-2">
          <Chip tone={computed.customsCompleteness >= 85 ? "success" : "warning"}>
            Completeness {computed.customsCompleteness}%
          </Chip>
          <Chip tone="success">Present {computed.customsCounts.present}</Chip>
          <Chip tone="accent">In-progress {computed.customsCounts["in-progress"]}</Chip>
          <Chip tone="danger">Missing {computed.customsCounts.missing}</Chip>
          <Chip tone="warning">Expired {computed.customsCounts.expired}</Chip>
        </div>

        <ScrollArea className="mt-3 h-[320px] pr-2">
          <div className="grid gap-2">
            {state.customsPack.map((document) => (
              <button
                key={document.id}
                type="button"
                onClick={() => actions.cycleCustomsDocStatus(document.id)}
                className="group cursor-pointer rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.86)] p-2.5 text-left transition-all hover:border-[hsl(var(--ui-accent)/0.45)]"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                    {document.label}
                  </p>
                  <div className="flex items-center gap-2">
                    <Chip tone={getCustomsStatusTone(document.status)}>
                      {document.status.toUpperCase()}
                    </Chip>
                    {document.critical ? <Chip tone="danger">CRITICAL</Chip> : null}
                  </div>
                </div>
                <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
                  Owner {document.owner.toUpperCase()} | Expiry {document.expiryDate}
                </p>
              </button>
            ))}
          </div>
        </ScrollArea>

        <div className="mt-3 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.45)] p-3">
          <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
            Gating conditions
          </p>
          <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
            {criticalMissing.length > 0 ? (
              <>
                {criticalMissing.map((document) => (
                  <li key={document.id}>
                    {document.label} is {document.status.toUpperCase()} and blocks RECEIVED state.
                  </li>
                ))}
              </>
            ) : (
              <li>All critical customs docs are present.</li>
            )}
            {computed.mismatchDetected ? (
              <li>Qty/Lot mismatch gate active until deviation ticket is completed.</li>
            ) : (
              <li>No quantity/lot mismatch detected.</li>
            )}
          </ul>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
