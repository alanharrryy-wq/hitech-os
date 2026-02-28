"use client";

import type {
  ActivityQueryResponse,
  RunsQueryResponse,
  WidgetsQueryResponse
} from "@hitech/contracts";
import { InsetPanel, Skeleton } from "@hitech/ui-kit";

export interface StatsPanelProps {
  readonly runs: RunsQueryResponse | undefined;
  readonly activity: ActivityQueryResponse | undefined;
  readonly widgets: WidgetsQueryResponse | undefined;
  readonly isLoading: boolean;
}

function deriveStats(input: {
  runs: RunsQueryResponse | undefined;
  activity: ActivityQueryResponse | undefined;
  widgets: WidgetsQueryResponse | undefined;
}): {
  totalRuns: number;
  runningRuns: number;
  failedRuns: number;
  criticalEvents: number;
  widgets: number;
} {
  const totalRuns = input.runs?.items.length ?? 0;
  const runningRuns = input.runs?.items.filter((item) => item.status === "running").length ?? 0;
  const failedRuns = input.runs?.items.filter((item) => item.status === "failed").length ?? 0;
  const criticalEvents =
    input.activity?.items.filter(
      (item) => item.severity === "critical" || item.severity === "error"
    ).length ?? 0;
  const widgets = input.widgets?.widgets.length ?? 0;

  return {
    totalRuns,
    runningRuns,
    failedRuns,
    criticalEvents,
    widgets
  };
}

function StatTile({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
      <p className="keystone-kicker">{label}</p>
      <p className="keystone-stat-value">{value}</p>
      <p className="m-0 text-xs keystone-muted">{hint}</p>
    </div>
  );
}

export function StatsPanel({ runs, activity, widgets, isLoading }: StatsPanelProps) {
  if (isLoading) {
    return (
      <InsetPanel title="Stats" description="Aggregates from contracts-validated data">
        <div className="grid grid-cols-2 gap-3">
          <Skeleton height={90} />
          <Skeleton height={90} />
          <Skeleton height={90} />
          <Skeleton height={90} />
        </div>
      </InsetPanel>
    );
  }

  const stats = deriveStats({ runs, activity, widgets });

  return (
    <InsetPanel title="Stats" description="Real-time summary from query state">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <StatTile
          label="Total Runs"
          value={String(stats.totalRuns)}
          hint="Across deterministic fixtures"
        />
        <StatTile label="Running" value={String(stats.runningRuns)} hint="Live execution now" />
        <StatTile label="Failed" value={String(stats.failedRuns)} hint="Needs attention" />
        <StatTile
          label="Critical Events"
          value={String(stats.criticalEvents)}
          hint="Errors + critical activity"
        />
        <StatTile
          label="Widgets"
          value={String(stats.widgets)}
          hint="Dashboard configuration nodes"
        />
      </div>
    </InsetPanel>
  );
}
