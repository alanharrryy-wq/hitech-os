import type { PitchScreen02 } from "@hitech/contracts";
import { GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import { CycleRing35 } from "./cycle-ring-35";
import { KpiRow } from "./kpi-row";
import { MicroCaption } from "./micro-caption";
import { PitchHeader } from "./pitch-header";
import { toIndustrialFlowModel } from "./types";

export interface ScreenIndustrialFlowProps {
  readonly screen: PitchScreen02;
}

export function ScreenIndustrialFlow({ screen }: ScreenIndustrialFlowProps) {
  const model = toIndustrialFlowModel(screen);

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 2",
              orderLabel: "02",
              title: model.title,
              subtitle: "Flujo industrial recurrente validado en mercado interno"
            }}
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title="KPIs operativos" description="Base de ejecución recurrente">
            <KpiRow
              items={model.kpis.map((kpi) => ({
                label: kpi.label,
                value: kpi.value,
                ...(kpi.note ? { note: kpi.note } : {})
              }))}
            />
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={8}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title="Ciclo de cobertura" description="Ciclo continuo de mantenimiento">
            <p className="m-0 text-base font-medium leading-7 text-[hsl(var(--ui-text-1))]">
              {model.cycleLabel}
            </p>
            <MicroCaption className="mt-3">{model.microcopy}</MicroCaption>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={4}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel title="Ritmo" description="35 meses">
            <CycleRing35 months={35} label="Ciclo continuo 35 meses" />
          </InsetPanel>
        </GlassCard>
      </GridItem>
    </Grid>
  );
}
