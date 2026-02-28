import { GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import { BulletList } from "./bullet-list";
import { DividerVertical } from "./divider-vertical";
import { MicroCaption } from "./micro-caption";
import { PitchHeader } from "./pitch-header";
import { SplitPane50 } from "./split-pane-50";
import { toDoubleEngineModel } from "./types";
import type { PitchScreen01 } from "@hitech/contracts";

export interface ScreenDoubleEngineProps {
  readonly screen: PitchScreen01;
}

export function ScreenDoubleEngine({ screen }: ScreenDoubleEngineProps) {
  const model = toDoubleEngineModel(screen);

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 1",
              orderLabel: "01",
              title: model.title,
              subtitle: "Arquitectura de doble motor para crecimiento operativo y digital"
            }}
          />
        </GlassCard>
      </GridItem>
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <SplitPane50
            divider={<DividerVertical label="vs" />}
            left={
              <InsetPanel title={model.left.heading} description="MOTOR 1">
                <BulletList bullets={model.left.bullets} />
                <div className="mt-3 grid gap-1">
                  {model.left.microcopy.map((line) => (
                    <MicroCaption key={line}>{line}</MicroCaption>
                  ))}
                </div>
              </InsetPanel>
            }
            right={
              <InsetPanel title={model.right.heading} description="MOTOR 2">
                <BulletList bullets={model.right.bullets} />
                <div className="mt-3 grid gap-1">
                  {model.right.microcopy.map((line) => (
                    <MicroCaption key={line}>{line}</MicroCaption>
                  ))}
                </div>
              </InsetPanel>
            }
          />
        </GlassCard>
      </GridItem>
      <GridItem span={12}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel title="Mensaje implícito" description="Posicionamiento estratégico">
            <p className="m-0 text-xl font-semibold tracking-[-0.01em] text-[hsl(var(--ui-text-1))]">
              {model.implicitMessage}
            </p>
          </InsetPanel>
        </GlassCard>
      </GridItem>
    </Grid>
  );
}
