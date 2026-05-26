"use client";

import type { LabChartEntry, LabChartFamily } from "@/prisma-charts/chart-lab-types";

type ExecutiveCommandPaletteProps = {
  open: boolean;
  charts: LabChartEntry[];
  activeChartId: string;
  query: string;
  onQueryChange: (query: string) => void;
  onClose: () => void;
  onSelectChart: (chartId: string) => void;
  onSetFamily: (family: LabChartFamily | "all") => void;
  onSetReadiness: (readiness: "all" | LabChartEntry["readiness"]) => void;
  onSetMode: (mode: "observatory" | "briefing" | "war-room") => void;
  onToggleFocus: () => void;
  onCopyBrief: () => void;
};

function matches(chart: LabChartEntry, query: string) {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return [chart.id, chart.title, chart.shortName, chart.description, chart.operationalQuestion, chart.family, chart.surface]
    .join(" ")
    .toLowerCase()
    .includes(needle);
}

export function ExecutiveCommandPalette({
  open,
  charts,
  activeChartId,
  query,
  onQueryChange,
  onClose,
  onSelectChart,
  onSetFamily,
  onSetReadiness,
  onSetMode,
  onToggleFocus,
  onCopyBrief
}: ExecutiveCommandPaletteProps) {
  if (!open) return null;

  const filteredCharts = charts.filter((chart) => matches(chart, query)).slice(0, 10);

  return (
    <div className="executive-command-palette" role="dialog" aria-modal="true" aria-label="Executive command palette" data-command-center-pro="palette">
      <button className="executive-command-palette__scrim" aria-label="Close command palette" type="button" onClick={onClose} />
      <section className="executive-command-palette__panel">
        <header>
          <span className="eyebrow">Command Palette</span>
          <h2>Navigate, brief, focus, filter</h2>
          <button type="button" onClick={onClose} aria-label="Close command palette">Esc</button>
        </header>
        <input
          autoFocus
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search chart, family, question, surface…"
          aria-label="Search command palette"
        />
        <div className="executive-command-palette__quick-actions" aria-label="Quick actions">
          <button type="button" onClick={() => onSetMode("observatory")}>Observatory mode</button>
          <button type="button" onClick={() => onSetMode("briefing")}>Briefing mode</button>
          <button type="button" onClick={() => onSetMode("war-room")}>War Room mode</button>
          <button type="button" onClick={onToggleFocus}>Toggle focus</button>
          <button type="button" onClick={onCopyBrief}>Copy executive brief</button>
          <button type="button" onClick={() => onSetReadiness("working")}>Only working</button>
          <button type="button" onClick={() => onSetReadiness("all")}>All readiness</button>
          <button type="button" onClick={() => onSetFamily("all")}>All families</button>
        </div>
        <div className="executive-command-palette__results" role="listbox" aria-label="Matching charts">
          {filteredCharts.map((chart) => (
            <button
              type="button"
              role="option"
              aria-selected={chart.id === activeChartId}
              key={chart.id}
              className={chart.id === activeChartId ? "is-active" : ""}
              onClick={() => {
                onSelectChart(chart.id);
                onClose();
              }}
            >
              <strong>{chart.shortName || chart.title}</strong>
              <span>{chart.family} · {chart.surface} · {chart.readiness} · {chart.confidence}%</span>
            </button>
          ))}
          {!filteredCharts.length ? <p>No chart matched that command query.</p> : null}
        </div>
      </section>
    </div>
  );
}
