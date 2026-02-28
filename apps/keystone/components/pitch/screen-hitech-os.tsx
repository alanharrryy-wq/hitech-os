import type { PitchScreen03 } from "@hitech/contracts";
import { GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import { FeatureCardGrid } from "./feature-card-grid";
import { PitchHeader } from "./pitch-header";
import { toHiTechOsModel } from "./types";

export interface ScreenHiTechOsProps {
  readonly screen: PitchScreen03;
}

export function ScreenHiTechOs({ screen }: ScreenHiTechOsProps) {
  const model = toHiTechOsModel(screen);

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 3",
              orderLabel: "03",
              title: model.title,
              subtitle: "Infraestructura digital propietaria con trazabilidad y control"
            }}
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title="Capacidades de plataforma" description="MOTOR 2 — HITECH OS">
            <FeatureCardGrid features={model.features} />
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel
            title="Línea estratégica"
            description="Enfoque de control de activos críticos"
          >
            <p className="m-0 text-lg font-semibold leading-7 text-[hsl(var(--ui-text-1))]">
              {model.strongLine}
            </p>
          </InsetPanel>
        </GlassCard>
      </GridItem>
    </Grid>
  );
}
