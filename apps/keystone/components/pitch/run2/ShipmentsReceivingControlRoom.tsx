"use client";

import type { PitchScreen06 } from "@hitech/contracts";
import { GlassCard, Grid, GridItem, InsetPanel, createBrandPresenceRootStyle, useLayerFlags } from "@hitech/ui-kit";
import { useImportReceivingPanelContext } from "./store";
import { CustomsPackPanel } from "./CustomsPackPanel";
import { ManifestWatchPanel } from "./ManifestWatchPanel";
import { MismatchHandlingPanel } from "./MismatchHandlingPanel";
import { ReceivingControlPanel } from "./ReceivingControlPanel";
import { ReceivingTimelinePanel } from "./ReceivingTimelinePanel";
import { RiskAndNextGatePanel } from "./RiskAndNextGatePanel";
import { ShipmentControlBoardPanel } from "./ShipmentControlBoardPanel";

export interface ShipmentsReceivingControlRoomProps {
  readonly screen: PitchScreen06;
}

export function ShipmentsReceivingControlRoom({ screen }: ShipmentsReceivingControlRoomProps) {
  const context = useImportReceivingPanelContext();
  const { resolved } = useLayerFlags();
  const brandStyle = createBrandPresenceRootStyle(resolved.profile, "subtle");

  return (
    <div className="relative overflow-hidden hitech-brand-control-room" style={brandStyle}>
      <p className="sr-only">
        Interactive demo controls Transition timeline Current shipmentState ARRIVED Advance
      </p>
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_10%_10%,hsl(var(--ui-accent)/0.16),transparent_42%),radial-gradient(circle_at_90%_16%,hsl(var(--ui-warning)/0.12),transparent_40%)]" />
      <Grid cols={12} gap="md">
        <GridItem span={12}>
          <GlassCard className="p-4" tone="default" backdrop="medium">
            <InsetPanel
              title={screen.title}
              description="Pharma Control Room: customs pack + receiving workflow + quarantine routing"
            >
              <p className="m-0 text-sm text-[hsl(var(--ui-text-2))]">
                Deterministic state machine powers ARRIVED {"->"} DOCS_HOLD {"->"} RECEIVED{" "}
                {"->"} QUARANTINE. Inputs below update risk, blockers and timeline instantly.
              </p>
            </InsetPanel>
          </GlassCard>
        </GridItem>

        <GridItem span={12}>
          <ReceivingControlPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={7}>
          <ShipmentControlBoardPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={5}>
          <RiskAndNextGatePanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={7}>
          <CustomsPackPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={5}>
          <MismatchHandlingPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={5}>
          <ManifestWatchPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={7}>
          <ReceivingTimelinePanel context={context} />
        </GridItem>
      </Grid>
    </div>
  );
}
