"use client";

import { Grid, GridItem, GlassCard, InsetPanel, Shell, Stage } from "@hitech/ui-kit";
import { useMemo } from "react";
import { useActivityQuery } from "../../lib/queries/activity";
import { useRunsQuery } from "../../lib/queries/runs";
import { useWidgetsQuery } from "../../lib/queries/widgets";
import { ActivityPanel } from "./activity-panel";
import { MissionHeader } from "./mission-header";
import { RunsPanel } from "./runs-panel";
import { StatsPanel } from "./stats-panel";
import { SystemPanel } from "./system-panel";

export function MissionControlView() {
  const runsQuery = useRunsQuery();
  const activityQuery = useActivityQuery();
  const widgetsQuery = useWidgetsQuery();

  const totals = useMemo(() => {
    const runs = runsQuery.data?.items ?? [];
    return {
      totalRuns: runs.length,
      runningRuns: runs.filter((item) => item.status === "running").length
    };
  }, [runsQuery.data]);

  return (
    <Stage fx={{ noise: false, scanline: false, haze: false, vignette: false }}>
      <Shell
        title="Keystone Mission Control"
        subtitle="Stage -> Shell -> Grid -> GlassCard -> InsetPanel architecture"
        actions={
          <p className="m-0 text-xs keystone-muted">
            Performance budgets respected: blur capped at 8px, shadow capped at var(--ui-shadow-max)
          </p>
        }
      >
        <MissionHeader totalRuns={totals.totalRuns} runningRuns={totals.runningRuns} />
        <Grid className="mt-6" gap="md" cols={12}>
          <GridItem span={12} spanLg={7}>
            <GlassCard className="p-3" backdrop="off" tone="default">
              <RunsPanel
                data={runsQuery.data}
                isLoading={runsQuery.isLoading}
                isError={runsQuery.isError}
              />
            </GlassCard>
          </GridItem>
          <GridItem span={12} spanLg={5}>
            <GlassCard className="p-3" backdrop="off" tone="default">
              <ActivityPanel
                data={activityQuery.data}
                isLoading={activityQuery.isLoading}
                isError={activityQuery.isError}
              />
            </GlassCard>
          </GridItem>
          <GridItem span={12} spanLg={7}>
            <GlassCard className="p-3" backdrop="off" tone="default">
              <StatsPanel
                runs={runsQuery.data}
                activity={activityQuery.data}
                widgets={widgetsQuery.data}
                isLoading={runsQuery.isLoading || activityQuery.isLoading || widgetsQuery.isLoading}
              />
            </GlassCard>
          </GridItem>
          <GridItem span={12} spanLg={5}>
            <GlassCard className="p-3" backdrop="off" tone="default">
              <SystemPanel
                data={widgetsQuery.data}
                isLoading={widgetsQuery.isLoading}
                isError={widgetsQuery.isError}
              />
            </GlassCard>
          </GridItem>
          <GridItem span={12}>
            <GlassCard className="p-3" backdrop="off" tone="muted">
              <InsetPanel
                title="System Notes"
                description="Neutral visual baseline only. Premium motion/fx hooks are intentionally disabled."
              >
                <ul className="m-0 grid gap-1 pl-4 text-sm text-[hsl(var(--ui-text-2))]">
                  <li>
                    Contracts enforce strict runtime validation for API outputs and query responses.
                  </li>
                  <li>Zustand stores only UI state (sidebar, selection, filters, theme mode).</li>
                  <li>TanStack Query is the only source of server state in the view.</li>
                  <li>
                    Radix primitives are integrated in ui-kit and available for progressive
                    enhancements.
                  </li>
                </ul>
              </InsetPanel>
            </GlassCard>
          </GridItem>
        </Grid>
      </Shell>
    </Stage>
  );
}
