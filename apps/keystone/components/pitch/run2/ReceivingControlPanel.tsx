"use client";

import { GlassCard, InsetPanel } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip, NeonButton } from "./primitives";
import { getReceivingStateTone } from "./store";

export interface ReceivingControlPanelProps {
  readonly context: ImportReceivingPanelContext;
}

export function ReceivingControlPanel({ context }: ReceivingControlPanelProps) {
  const { state, computed, actions } = context;
  const transition = computed.transition;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Receiving Control Panel"
        description="Interactive demo controls: Advance / Reset / Force Quarantine"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <p className="m-0 text-xs text-[hsl(var(--ui-text-3))]">Current shipmentState</p>
            <Chip tone={getReceivingStateTone(state.shipmentState)}>{state.shipmentState}</Chip>
            <Chip tone={transition.allowed ? "success" : "warning"}>
              NEXT {transition.nextState}
            </Chip>
            <Chip tone={computed.mismatchDetected ? "danger" : "success"}>
              {computed.mismatchDetected ? "MISMATCH" : "MATCHED"}
            </Chip>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <NeonButton onClick={actions.advance}>Advance</NeonButton>
            <NeonButton variant="outline" onClick={actions.reset}>
              Reset
            </NeonButton>
            <NeonButton variant="outline" onClick={actions.forceQuarantine}>
              Force quarantine
            </NeonButton>
          </div>
        </div>

        <div className="mt-3 rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.4)] p-3">
          <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
            Transition guard
          </p>
          <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
            {transition.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
