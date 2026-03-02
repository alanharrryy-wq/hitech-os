"use client";

import type { PitchScreen05 } from "@hitech/contracts";
import { GlassCard, Grid, GridItem, InsetPanel, createBrandPresenceRootStyle, useLayerFlags } from "@hitech/ui-kit";
import { useInventoryFoundationPanelContext } from "./store";
import { DocumentVaultPanel } from "./DocumentVaultPanel";
import { FoundationActivityPanel } from "./FoundationActivityPanel";
import { FoundationDashboard } from "./FoundationDashboard";
import { LiveFieldPanel } from "./LiveFieldPanel";
import { RBACMatrixPanel } from "./RBACMatrixPanel";
import { ReadinessScorePanel } from "./ReadinessScorePanel";
import { SupplierStatusPanel } from "./SupplierStatusPanel";

export interface InventoryFoundationControlRoomProps {
  readonly screen: PitchScreen05;
}

export function InventoryFoundationControlRoom({ screen }: InventoryFoundationControlRoomProps) {
  const context = useInventoryFoundationPanelContext();
  const { resolved } = useLayerFlags();
  const brandStyle = createBrandPresenceRootStyle(resolved.profile, "subtle");

  return (
    <div className="relative overflow-hidden hitech-brand-control-room" style={brandStyle}>
      <p className="sr-only">Interactive demo controls Proceed to Shipments HOLD</p>
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_15%_20%,hsl(var(--ui-accent)/0.16),transparent_42%),radial-gradient(circle_at_85%_0%,hsl(var(--ui-success)/0.12),transparent_36%)]" />
      <Grid cols={12} gap="md">
        <GridItem span={12}>
          <GlassCard className="p-4" tone="default" backdrop="medium">
            <InsetPanel
              title={screen.title}
              description="Pharma Control Room: RBAC + supplier + SKU + document vault interactive gate"
            >
              <p className="m-0 text-sm text-[hsl(var(--ui-text-2))]">
                Canonical copy lock respected. Runtime inputs below are deterministic and drive
                immediate readiness, gate and hold decisions.
              </p>
            </InsetPanel>
          </GlassCard>
        </GridItem>

        <GridItem span={12}>
          <FoundationDashboard context={context} />
        </GridItem>

        <GridItem span={12}>
          <LiveFieldPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={7}>
          <RBACMatrixPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={5}>
          <ReadinessScorePanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={7}>
          <DocumentVaultPanel context={context} />
        </GridItem>

        <GridItem span={12} spanLg={5}>
          <SupplierStatusPanel context={context} />
        </GridItem>

        <GridItem span={12}>
          <FoundationActivityPanel context={context} />
        </GridItem>
      </Grid>
    </div>
  );
}
