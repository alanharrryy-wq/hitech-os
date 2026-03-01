"use client";

import type { PitchScreen06 } from "@hitech/contracts";
import type { BadgeProps } from "@hitech/ui-kit";
import { Badge, Button, GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import { DEMO_DOCUMENTS, formatDocumentLifecycleLabel } from "../../lib/pitch/demo-state";
import { BulletList } from "./bullet-list";
import { PitchDemoControlPanel } from "./pitch-demo-control-panel";
import { PitchDemoGuardBadges } from "./pitch-demo-guard-badges";
import { PitchHeader } from "./pitch-header";
import { toShipmentsReceivingModel } from "./types";
import { usePitchDemoController } from "./use-pitch-demo-controller";

type PitchStatus = PitchScreen06["shipmentControlBoard"]["customsPackCompleteness"]["status"];
type ReceivingStateCode = PitchScreen06["receivingFlow"]["states"][number]["code"];

const STATUS_TONE: Record<PitchStatus, NonNullable<BadgeProps["tone"]>> = {
  DONE: "success",
  IN_PROGRESS: "warning",
  PENDING: "neutral",
  MISSING: "danger"
};

const RECEIVING_TONE: Record<ReceivingStateCode, NonNullable<BadgeProps["tone"]>> = {
  ARRIVED: "accent",
  DOCS_HOLD: "warning",
  RECEIVED: "success",
  QUARANTINE: "danger"
};

function statusLabel(status: PitchStatus): string {
  return status.toLowerCase().replaceAll("_", " ");
}

export interface ScreenShipmentsReceivingProps {
  readonly screen: PitchScreen06;
}

export function ScreenShipmentsReceiving({ screen }: ScreenShipmentsReceivingProps) {
  const model = toShipmentsReceivingModel(screen);
  const demo = usePitchDemoController({
    shipmentState: "ARRIVED",
    documents: {
      COA: "PRESENT",
      TEMP_REPORT: "PRESENT",
      IMPORT_PERMIT: "PRESENT"
    }
  });

  const isQuarantine = demo.state.shipmentState === "QUARANTINE";

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 6",
              orderLabel: "06",
              title: model.title,
              subtitle: "Interactive receiving demo with deterministic state transitions"
            }}
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={7}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchDemoControlPanel
            state={demo.state}
            onRoleChange={demo.setRole}
            onSupplierStatusChange={demo.setSupplierStatus}
            onToggleDocumentLifecycle={demo.toggleDocumentLifecycle}
            onTempExcursionChange={demo.setTempExcursion}
            extraActions={
              <div className="flex flex-wrap items-center justify-end gap-2">
                <Button size="sm" onClick={demo.advance}>
                  Advance
                </Button>
                <Button variant="outline" size="sm" onClick={demo.reset}>
                  Reset
                </Button>
                <Button variant="outline" size="sm" onClick={demo.forceQuarantine}>
                  Force quarantine
                </Button>
              </div>
            }
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={5}>
        <GlassCard className="p-4" tone={isQuarantine ? "raised" : "default"} backdrop="off">
          <InsetPanel
            title="Shipment runtime state"
            description="State machine output + guard snapshot"
          >
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
              <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
                Current shipmentState
              </p>
              <Badge tone={RECEIVING_TONE[demo.state.shipmentState]}>
                {demo.state.shipmentState}
              </Badge>
            </div>
            <div className="mt-3">
              <PitchDemoGuardBadges guards={demo.guards} />
            </div>
            {isQuarantine ? (
              <p className="m-0 mt-3 rounded-lg border border-[hsl(var(--ui-danger))] bg-[hsl(var(--ui-danger)/0.08)] p-3 text-sm font-semibold text-[hsl(var(--ui-danger))]">
                QUARANTINE is active. Temperature excursion or manual quarantine has locked
                receiving.
              </p>
            ) : null}
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title="Transition timeline"
            description="Deterministic transitionLog from applyAction()"
          >
            <ol className="m-0 grid list-none gap-2 p-0">
              {demo.state.transitionLog.map((entry) => (
                <li
                  key={entry.id}
                  className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Badge tone="neutral">#{entry.sequence}</Badge>
                      <Badge tone="accent">{entry.action}</Badge>
                    </div>
                    <Badge tone={RECEIVING_TONE[entry.to]}>
                      {entry.from} → {entry.to}
                    </Badge>
                  </div>
                  <p className="m-0 mt-2 text-xs text-[hsl(var(--ui-text-2))]">{entry.reason}</p>
                </li>
              ))}
            </ol>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={7}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title={model.shipmentControlBoard.heading}
            description="AWB/BL, ETA/ATA and Incoterm control board"
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {model.shipmentControlBoard.fields.map((field) => (
                <article
                  key={field.label}
                  className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
                    {field.label}
                  </p>
                  <p className="m-0 mt-2 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                    {field.value}
                  </p>
                </article>
              ))}
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={5}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title="Customs pack checklist"
            description={model.customsPackChecklist.heading}
          >
            <div className="flex items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
              <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
                Overall
              </p>
              <Badge tone={demo.guards.docs_complete ? "success" : "warning"}>
                {demo.guards.docs_complete ? "docs complete" : "docs hold"}
              </Badge>
            </div>
            <div className="mt-3 grid gap-2">
              {DEMO_DOCUMENTS.map((document) => {
                const lifecycle = demo.state.documents[document.id];
                return (
                  <article
                    key={document.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                  >
                    <p className="m-0 text-sm text-[hsl(var(--ui-text-1))]">{document.label}</p>
                    <Badge tone={lifecycle === "PRESENT" ? "success" : "danger"}>
                      {formatDocumentLifecycleLabel(lifecycle)}
                    </Badge>
                  </article>
                );
              })}
              {model.customsPackChecklist.items.map((item) => (
                <article
                  key={item.label}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <p className="m-0 text-sm text-[hsl(var(--ui-text-1))]">{item.label}</p>
                  <Badge tone={STATUS_TONE[item.status]}>{statusLabel(item.status)}</Badge>
                </article>
              ))}
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title={model.receivingFlow.heading}
            description="ARRIVED -> DOCS_HOLD -> RECEIVED -> QUARANTINE"
          >
            <div className="grid gap-3 lg:grid-cols-4">
              {model.receivingFlow.states.map((state) => (
                <article
                  key={state.code}
                  className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <div className="flex items-center justify-between gap-2">
                    <Badge tone="neutral">Step {state.order}</Badge>
                    <Badge tone={RECEIVING_TONE[state.code]}>
                      {state.code}
                      {demo.state.shipmentState === state.code ? " (current)" : ""}
                    </Badge>
                  </div>
                  <p className="m-0 mt-2 text-xs text-[hsl(var(--ui-text-2))]">{state.note}</p>
                </article>
              ))}
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={8}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title={model.mismatchHandling.heading}
            description="Qty/lot mismatch handling"
          >
            <BulletList
              bullets={[
                model.mismatchHandling.qtyLotMismatch,
                `Deviation placeholder: ${model.mismatchHandling.deviationPlaceholder}`
              ]}
              itemClassName="text-sm leading-6"
            />
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={4}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel title="Next gate" description="QA Release (RUN3)">
            <p className="m-0 text-sm font-semibold leading-6 text-[hsl(var(--ui-text-1))]">
              {model.nextGate}
            </p>
          </InsetPanel>
        </GlassCard>
      </GridItem>
    </Grid>
  );
}
