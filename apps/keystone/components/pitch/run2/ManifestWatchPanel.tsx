"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext } from "./types";
import { Chip } from "./primitives";
import { getReceivingStateTone } from "./store";

export interface ManifestWatchPanelProps {
  readonly context: ImportReceivingPanelContext;
}

function riskTone(risk: "low" | "medium" | "high"): "success" | "warning" | "danger" {
  if (risk === "low") {
    return "success";
  }
  if (risk === "medium") {
    return "warning";
  }
  return "danger";
}

export function ManifestWatchPanel({ context }: ManifestWatchPanelProps) {
  const { state, actions } = context;

  return (
    <GlassCard className="p-4" tone="muted" backdrop="medium">
      <InsetPanel
        title="Manifest Watch Panel"
        description="Deterministic manifest registry tied to shipment board fields"
      >
        <ScrollArea className="h-[280px] pr-2">
          <div className="grid gap-2">
            {state.manifests.slice(0, 220).map((manifest) => (
              <button
                key={manifest.id}
                type="button"
                onClick={() => actions.setSelectedManifest(manifest.id)}
                className="cursor-pointer rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.88)] p-2.5 text-left transition-colors hover:border-[hsl(var(--ui-accent)/0.45)]"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="m-0 text-xs font-semibold text-[hsl(var(--ui-text-1))]">
                    {manifest.id} | {manifest.awbBl}
                  </p>
                  <div className="flex items-center gap-2">
                    <Chip tone={getReceivingStateTone(manifest.status)}>{manifest.status}</Chip>
                    <Chip tone={riskTone(manifest.laneRisk)}>{manifest.laneRisk}</Chip>
                  </div>
                </div>
                <p className="m-0 mt-1 text-[11px] text-[hsl(var(--ui-text-2))]">
                  {manifest.product} | {manifest.origin} {"->"} {manifest.destinationPort}
                </p>
              </button>
            ))}
          </div>
        </ScrollArea>
      </InsetPanel>
    </GlassCard>
  );
}
