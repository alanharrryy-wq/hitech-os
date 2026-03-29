"use client";

import { GlassCard, InsetPanel } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip } from "./primitives";

export interface MismatchHandlingPanelProps {
  readonly context: ImportReceivingPanelContext;
}

export function MismatchHandlingPanel({ context }: MismatchHandlingPanelProps) {
  const { state, computed } = context;
  const ticket = state.deviationTicket;
  const qtyMismatch = state.fields.quantityDeclared !== state.fields.quantityReceived;
  const lotMismatch =
    state.fields.lotDeclared.trim().toLowerCase() !== state.fields.lotReceived.trim().toLowerCase();

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Mismatch Handling Panel"
        description="Qty/Lot mismatch creates deterministic deviation ticket and next-step checklist"
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <article className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.9)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">Qty mismatch</p>
              <Chip tone={qtyMismatch ? "danger" : "success"}>{qtyMismatch ? "YES" : "NO"}</Chip>
            </div>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              Declared {state.fields.quantityDeclared} vs Received {state.fields.quantityReceived}
            </p>
          </article>

          <article className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.9)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">Lot mismatch</p>
              <Chip tone={lotMismatch ? "danger" : "success"}>{lotMismatch ? "YES" : "NO"}</Chip>
            </div>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              Declared {state.fields.lotDeclared} vs Received {state.fields.lotReceived}
            </p>
          </article>
        </div>

        {ticket ? (
          <div className="mt-3 rounded-xl border border-[hsl(var(--ui-danger))] bg-[hsl(var(--ui-danger)/0.09)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                Deviation ticket {ticket.id}
              </p>
              <Chip tone="danger">{ticket.severity.toUpperCase()}</Chip>
            </div>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              Category {ticket.category} | Created {ticket.createdAt}
            </p>
            <ul className="m-0 mt-2 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
              {ticket.requiredSteps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="m-0 mt-3 rounded-xl border border-[hsl(var(--ui-success))] bg-[hsl(var(--ui-success)/0.08)] p-3 text-sm text-[hsl(var(--ui-success))]">
            No deviation ticket active. Shipment can proceed if customs and risk gates are clean.
          </p>
        )}

        <div className="mt-3 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.4)] p-3">
          <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
            Why this gate is {computed.nextGate.state}
          </p>
          <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
            {computed.nextGate.blockers.length > 0 ? (
              computed.nextGate.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)
            ) : (
              <li>All blockers cleared.</li>
            )}
          </ul>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
