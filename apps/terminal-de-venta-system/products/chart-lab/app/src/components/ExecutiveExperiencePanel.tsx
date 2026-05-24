"use client";

import type { LabChartEntry } from "@/prisma-charts/chart-lab-types";

type ExecutiveExperiencePanelProps = {
  selectedChart: LabChartEntry;
  totalCharts: number;
  workingCharts: number;
  placeholderCharts: number;
  activeControls: number;
  commandMode: string;
  focusMode: boolean;
  publicSafe: boolean;
  onToggleFocus: () => void;
  onOpenPalette: () => void;
  onCopyBrief: () => void;
  onJumpToControls: () => void;
};

function dataStatusTone(status: string) {
  if (status.includes("runtime")) return "runtime";
  if (status.includes("partial")) return "partial";
  if (status.includes("stale")) return "stale";
  if (status.includes("invalid") || status.includes("unavailable")) return "risk";
  return "mock";
}

function readinessCopy(chart: LabChartEntry) {
  if (chart.readiness === "working") return "Ready for executive review";
  if (chart.readiness === "placeholder") return "Design placeholder, not release grade";
  return chart.unavailableReason ?? "Unavailable in this build";
}

export function ExecutiveExperiencePanel({
  selectedChart,
  totalCharts,
  workingCharts,
  placeholderCharts,
  activeControls,
  commandMode,
  focusMode,
  publicSafe,
  onToggleFocus,
  onOpenPalette,
  onCopyBrief,
  onJumpToControls
}: ExecutiveExperiencePanelProps) {
  const statusTone = dataStatusTone(String(selectedChart.dataStatus ?? ""));
  const coverage = Math.round((workingCharts / Math.max(totalCharts, 1)) * 100);
  const designDebt = Math.max(totalCharts - workingCharts - placeholderCharts, 0);

  return (
    <section className="executive-experience-panel" aria-label="Executive experience controls" data-command-center-pro="experience-panel">
      <div className="executive-experience-panel__summary">
        <span className="eyebrow">Experience command rail</span>
        <h2>{selectedChart.shortName || selectedChart.title}</h2>
        <p>{readinessCopy(selectedChart)} · {selectedChart.freshnessLabel} · {selectedChart.confidence}% confidence.</p>
      </div>

      <div className="executive-experience-panel__meters" aria-label="Readiness overview">
        <article data-tone="ready">
          <span>{coverage}%</span>
          <small>Working coverage</small>
        </article>
        <article data-tone={statusTone}>
          <span>{selectedChart.dataStatus}</span>
          <small>Data posture</small>
        </article>
        <article data-tone={activeControls ? "active" : "calm"}>
          <span>{activeControls}</span>
          <small>Active controls</small>
        </article>
        <article data-tone={publicSafe ? "safe" : "local"}>
          <span>{publicSafe ? "Public safe" : "Local"}</span>
          <small>Deployment posture</small>
        </article>
        <article data-tone={designDebt ? "watch" : "ready"}>
          <span>{designDebt}</span>
          <small>Unavailable debt</small>
        </article>
      </div>

      <div className="executive-experience-panel__actions" aria-label="Executive actions">
        <button type="button" onClick={onOpenPalette} data-command-action="palette">⌘K Palette</button>
        <button type="button" onClick={onToggleFocus} aria-pressed={focusMode} data-command-action="focus">{focusMode ? "Exit Focus" : "Focus Mode"}</button>
        <button type="button" onClick={onCopyBrief} data-command-action="copy-brief">Copy Brief</button>
        <button type="button" onClick={onJumpToControls} data-command-action="controls">Tune Controls</button>
      </div>

      <div className="executive-experience-panel__hints" aria-label="Keyboard shortcuts">
        <span>Mode: {commandMode}</span>
        <span><kbd>Ctrl</kbd><kbd>K</kbd> palette</span>
        <span><kbd>F</kbd> focus</span>
        <span><kbd>?</kbd> shortcuts</span>
      </div>
    </section>
  );
}
