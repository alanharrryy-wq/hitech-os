import type { PropsWithChildren, ReactNode } from "react";
import { Grid, GridItem, Shell, Stage, cn } from "@hitech/ui-kit";
import type { PitchNavModel } from "./types";
import { PitchNav } from "./pitch-nav";

export interface PitchShellProps extends PropsWithChildren {
  readonly title: string;
  readonly subtitle?: string;
  readonly nav: PitchNavModel;
  readonly actions?: ReactNode;
  readonly className?: string;
}

export function PitchShell({
  title,
  subtitle,
  nav,
  actions,
  children,
  className
}: PitchShellProps) {
  return (
    <Stage className="pitch-stage">
      <Shell
        title={title}
        subtitle={subtitle}
        actions={actions}
        width="default"
        className={cn("pb-12", className)}
      >
        <Grid cols={12} gap="md">
          <GridItem span={12}>
            <PitchNav model={nav} />
          </GridItem>
          <GridItem span={12}>{children}</GridItem>
        </Grid>
      </Shell>
    </Stage>
  );
}
