"use client";

import { GlassCard, InsetPanel } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip } from "./primitives";

export interface RiskAndNextGatePanelProps {
  readonly context: ImportReceivingPanelContext;
}

function riskTone(level: "low" | "medium" | "high"): "success" | "warning" | "danger" {
  if (level === "low") {
    return "success";
  }
  if (level === "medium") {
    return "warning";
  }
  return "danger";
}

function nextGateTone(state: "READY" | "HOLD" | "BLOCKED"): "success" | "warning" | "danger" {
  if (state === "READY") {
    return "success";
  }
  if (state === "HOLD") {
    return "warning";
  }
  return "danger";
}

export function RiskAndNextGatePanel({ context }: RiskAndNextGatePanelProps) {
  const { computed } = context;
  const risk = computed.riskPanel;
  const nextGate = computed.nextGate;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Risk And Next Gate Panel"
        description="Risk score and progression blockers from live shipment edits"
      >
        <div className="grid gap-3">
          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.88)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">Operational risk</p>
              <Chip tone={riskTone(risk.level)}>
                {risk.level.toUpperCase()} {risk.score}
              </Chip>
            </div>
            <ul className="m-0 mt-2 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
              {risk.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </article>

          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.88)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">{nextGate.title}</p>
              <Chip tone={nextGateTone(nextGate.state)}>{nextGate.state}</Chip>
            </div>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              <section className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.45)] p-2.5">
                <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
                  Blockers
                </p>
                <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
                  {nextGate.blockers.length > 0 ? (
                    nextGate.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)
                  ) : (
                    <li>No blockers detected.</li>
                  )}
                </ul>
              </section>
              <section className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.45)] p-2.5">
                <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
                  Next actions
                </p>
                <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
                  {nextGate.nextActions.length > 0 ? (
                    nextGate.nextActions.map((action) => <li key={action}>{action}</li>)
                  ) : (
                    <li>No additional action required.</li>
                  )}
                </ul>
              </section>
            </div>
          </article>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
