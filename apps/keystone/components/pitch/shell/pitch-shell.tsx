import type { PropsWithChildren } from "react";
import { Grid, GridItem, Shell, Stage, cn } from "@hitech/ui-kit";
import { PitchRailNav } from "../nav/pitch-rail-nav";
import { PitchShellBreadcrumbs } from "./pitch-shell-breadcrumbs";
import { PitchHero } from "./pitch-hero";
import { PitchShellProgress } from "./pitch-shell-progress";
import type { PitchShellProps } from "./types";
import { PitchShellKeyboardNav } from "./pitch-shell-keyboard-nav";
import { PitchScrollAffordance } from "./pitch-scroll-affordance";
import { PitchSectionProvider } from "./pitch-shell-context";
import { PitchLayerEffects } from "./pitch-layer-effects";
import { PitchShellBrandLayer } from "./pitch-shell-brand-layer";

export function PitchShell({
  model,
  children,
  className,
  showScrollAffordance = true,
  enableKeyboardNav = false
}: PropsWithChildren<PitchShellProps>) {
  return (
    <Stage
      className={cn("pitch-stage pitch-shell-root pb-16", className)}
      data-pitch-screen={model.nav.activeSlug ?? "pitch-index"}
    >
      <PitchShellBrandLayer />
      <PitchShellKeyboardNav links={model.nav.links} disabled={!enableKeyboardNav} />
      <Shell
        title={model.hero.title}
        subtitle={model.hero.subtitle}
        width="default"
        className="relative z-10"
      >
        <PitchSectionProvider>
          <Grid cols={12} gap="md">
            <GridItem span={12}>
              <PitchShellBreadcrumbs items={model.breadcrumbs} />
            </GridItem>

            <GridItem span={12}>
              <PitchLayerEffects>
                <PitchHero model={model.hero} />
              </PitchLayerEffects>
            </GridItem>

            <GridItem span={12}>
              <PitchLayerEffects>
                <PitchRailNav model={model.nav} progress={model.progress} />
              </PitchLayerEffects>
            </GridItem>

            <GridItem span={12} spanLg={9}>
              <PitchLayerEffects className="grid gap-4">{children}</PitchLayerEffects>
            </GridItem>

            <GridItem span={12} spanLg={3}>
              <aside className="grid gap-4 lg:sticky lg:top-4">
                <PitchLayerEffects>
                  <PitchShellProgress model={model.progress} />
                </PitchLayerEffects>
              </aside>
            </GridItem>
          </Grid>
        </PitchSectionProvider>
      </Shell>
      {showScrollAffordance ? <PitchScrollAffordance /> : null}
    </Stage>
  );
}
