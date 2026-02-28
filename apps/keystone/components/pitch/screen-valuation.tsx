import type { PitchScreen04 } from "@hitech/contracts";
import { GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import { ComparisonTable } from "./comparison-table";
import { PitchHeader } from "./pitch-header";
import { ValuationBlocks } from "./valuation-blocks";
import { toValuationModel } from "./types";

export interface ScreenValuationProps {
  readonly screen: PitchScreen04;
}

export function ScreenValuation({ screen }: ScreenValuationProps) {
  const model = toValuationModel(screen);

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 4",
              orderLabel: "04",
              title: model.title,
              subtitle: "Flujo + software propietario para múltiplo superior"
            }}
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <ValuationBlocks blocks={model.blocks} />
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel
            title="Valuación combinada"
            description="Resultado esperado del modelo integrado"
          >
            <p className="m-0 text-xl font-semibold text-[hsl(var(--ui-text-1))]">
              {model.combinedLine}
            </p>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <ComparisonTable headers={model.comparisonHeaders} rows={model.comparisonRows} />
      </GridItem>
    </Grid>
  );
}
