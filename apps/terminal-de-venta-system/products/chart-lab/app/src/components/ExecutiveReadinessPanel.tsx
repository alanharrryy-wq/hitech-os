"use client";

import type { LabChartEntry } from "@/prisma-charts/chart-lab-types";

type ExecutiveReadinessPanelProps = {
  charts: LabChartEntry[];
  selectedChart: LabChartEntry;
  publicSafe: boolean;
  activeControls: number;
  commandMode: string;
};

function countBy<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, item) => {
    acc[item] = (acc[item] ?? 0) + 1;
    return acc;
  }, {});
}

function statusTone(value: string) {
  if (value.includes("runtime")) return "ready";
  if (value.includes("partial")) return "watch";
  if (value.includes("stale")) return "stale";
  if (value.includes("invalid") || value.includes("unavailable")) return "risk";
  return "neutral";
}

export function ExecutiveReadinessPanel({ charts, selectedChart, publicSafe, activeControls, commandMode }: ExecutiveReadinessPanelProps) {
  const readiness = countBy(charts.map((chart) => chart.readiness));
  const dataStatus = countBy(charts.map((chart) => chart.dataStatus));
  const avgConfidence = Math.round(charts.reduce((sum, chart) => sum + chart.confidence, 0) / Math.max(charts.length, 1));
  const releaseScore = Math.min(100, Math.round(((readiness.working ?? 0) / Math.max(charts.length, 1)) * 65 + avgConfidence * 0.35));
  const blockers = charts.filter((chart) => chart.readiness === "unavailable" || chart.dataStatus === "invalid" || chart.dataStatus === "unavailable");
  const stale = charts.filter((chart) => chart.dataStatus === "stale");

  return (
    <section className="executive-readiness-panel" aria-label="Release and visual QA readiness" data-command-center-pro="readiness-panel">
      <header>
        <span className="eyebrow">Release readiness</span>
        <h3>{releaseScore}% command confidence</h3>
        <p>{publicSafe ? "Public-safe posture is active." : "Local atelier mode. Re-run public-safe verification before deploy."}</p>
      </header>
      <div className="executive-readiness-panel__grid">
        <article data-tone="ready"><strong>{readiness.working ?? 0}</strong><span>Working</span></article>
        <article data-tone="watch"><strong>{readiness.placeholder ?? 0}</strong><span>Templates</span></article>
        <article data-tone={blockers.length ? "risk" : "ready"}><strong>{blockers.length}</strong><span>Blockers</span></article>
        <article data-tone={stale.length ? "stale" : "ready"}><strong>{stale.length}</strong><span>Stale</span></article>
      </div>
      <div className="executive-readiness-panel__status-stack">
        {Object.entries(dataStatus).map(([status, count]) => (
          <span key={status} data-tone={statusTone(status)}>{status}: {count}</span>
        ))}
      </div>
      <footer>
        <span>Selected: {selectedChart.shortName || selectedChart.title}</span>
        <span>{activeControls} active controls</span>
        <span>{commandMode}</span>
      </footer>
    </section>
  );
}
