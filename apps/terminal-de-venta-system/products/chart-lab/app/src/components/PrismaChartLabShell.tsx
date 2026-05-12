"use client";

import { useMemo, useState } from "react";
import { ChartControlDeck } from "@/components/ChartControlDeck";
import { LabEChartFrame } from "@/prisma-charts/components/LabEChartFrame";
import { applyChartLabControls, countActiveControls, getControlsForChart, getDefaultControlState } from "@/prisma-charts/chart-lab-control-model";
import { chartLabFamilies, chartLabRegistry, chartLabSurfaces, chartOpsChartIds } from "@/prisma-charts/chart-lab-registry";
import {
  chartLabMapCatalog,
  dataSourceMap,
  humanIntentMap,
  promotionManifestMap,
  routeMap,
  stateGalleryMap,
  surfaceTransportMap,
  validationMap,
  visualTuningPassports
} from "@/prisma-charts/maps/chart-lab-maps";
import type {
  LabChartControlState,
  LabChartControlValue,
  LabChartDensity,
  LabChartEntry,
  LabChartInspectorTab,
  LabChartPreviewFrame,
  LabChartSize,
  LabChartThemeMode
} from "@/prisma-charts/chart-lab-types";

type SurfaceFilter = (typeof chartLabSurfaces)[number];
type FamilyFilter = (typeof chartLabFamilies)[number];
type ReadinessFilter = "all" | LabChartEntry["readiness"];

const inspectorTabs: Array<{ id: LabChartInspectorTab; label: string }> = [
  { id: "preview", label: "Preview" },
  { id: "controls", label: "Controls" },
  { id: "passport", label: "Passport" },
  { id: "maps", label: "Maps" },
  { id: "data", label: "Sources" },
  { id: "promotion", label: "Promotion" },
  { id: "intent", label: "Intent" },
  { id: "states", label: "States" },
  { id: "health", label: "Health" }
];

function surfaceLabel(surface: LabChartEntry["surface"]) {
  if (surface === "pc") return "PC governs";
  if (surface === "tablet") return "Tablet operates";
  if (surface === "mobile") return "Mobile supervises";
  return "Web / future";
}

function readinessTone(readiness: LabChartEntry["readiness"]) {
  if (readiness === "working") return "ready";
  if (readiness === "placeholder") return "draft";
  return "blocked";
}

function asArray<T>(value: T | T[] | null | undefined): T[] {
  if (Array.isArray(value)) return value;
  return value === null || value === undefined ? [] : [value];
}

function summarizeJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function chartConfigPayload(input: {
  chart: LabChartEntry;
  controls: LabChartControlState;
  density: LabChartDensity;
  size: LabChartSize;
  frame: LabChartPreviewFrame;
  publicSafe: boolean;
  deploymentMode: string;
}) {
  return {
    schemaVersion: "1.0",
    generatedAt: new Date().toISOString(),
    chartId: input.chart.id,
    surface: input.chart.surface,
    family: input.chart.family,
    dataMode: "mock/demo",
    publicSafe: input.publicSafe,
    deploymentMode: input.deploymentMode,
    preview: {
      density: input.density,
      size: input.size,
      frame: input.frame
    },
    controls: input.controls
  };
}

export function PrismaChartLabShell() {
  const publicSafe = process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE === "true";
  const deploymentMode = process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE ?? "local";
  const [selectedId, setSelectedId] = useState(chartLabRegistry[0]?.id ?? "");
  const [surface, setSurface] = useState<SurfaceFilter>("all");
  const [family, setFamily] = useState<FamilyFilter>("all");
  const [readiness, setReadiness] = useState<ReadinessFilter>("all");
  const [search, setSearch] = useState("");
  const [themeMode, setThemeMode] = useState<LabChartThemeMode>("prisma-crystal");
  const [density, setDensity] = useState<LabChartDensity>("calm");
  const [size, setSize] = useState<LabChartSize>("focus");
  const [frame, setFrame] = useState<LabChartPreviewFrame>("pc");
  const [minimumConfidence, setMinimumConfidence] = useState(0);
  const [tab, setTab] = useState<LabChartInspectorTab>("preview");
  const [pinnedIds, setPinnedIds] = useState<string[]>([]);
  const [recentIds, setRecentIds] = useState<string[]>([]);
  const [controlStateByChart, setControlStateByChart] = useState<Record<string, LabChartControlState>>({});
  const [copyStatus, setCopyStatus] = useState("idle");

  const filteredCharts = useMemo(
    () =>
      chartLabRegistry.filter((chart) => {
        const surfaceMatches = surface === "all" || chart.surface === surface;
        const familyMatches = family === "all" || chart.family === family;
        const readinessMatches = readiness === "all" || chart.readiness === readiness;
        const confidenceMatches = chart.confidence >= minimumConfidence;
        const normalizedSearch = search.trim().toLowerCase();
        const searchMatches =
          normalizedSearch.length === 0 ||
          [chart.id, chart.title, chart.shortName, chart.operationalQuestion, chart.description].some((value) =>
            value.toLowerCase().includes(normalizedSearch)
          );
        return surfaceMatches && familyMatches && readinessMatches && confidenceMatches && searchMatches;
      }),
    [family, minimumConfidence, readiness, search, surface]
  );

  const selectedChart = filteredCharts.find((chart) => chart.id === selectedId) ?? filteredCharts[0] ?? chartLabRegistry[0];
  const selectedControls = getControlsForChart(selectedChart.id);
  const selectedControlState = { ...getDefaultControlState(selectedChart.id), ...(controlStateByChart[selectedChart.id] ?? {}) };
  const workingCount = chartLabRegistry.filter((chart) => chart.readiness === "working").length;
  const placeholderCount = chartLabRegistry.filter((chart) => chart.readiness === "placeholder").length;
  const activeControls = countActiveControls(selectedChart.id, selectedControlState);
  const selectedPassport = visualTuningPassports.find((item) => item.chartId === selectedChart.id);
  const selectedDataSource = dataSourceMap.find((item) => item.chartId === selectedChart.id);
  const selectedTransport = surfaceTransportMap.find((item) => item.chartId === selectedChart.id);
  const selectedPromotion = promotionManifestMap.find((item) => item.chartId === selectedChart.id);
  const selectedRoute = routeMap.find((item) => item.chartId === selectedChart.id);
  const selectedStates = stateGalleryMap.find((item) => item.chartId === selectedChart.id);

  const optionOverride = useMemo(() => {
    const baseOption = selectedChart.getOption?.();
    if (!baseOption) return undefined;
    return applyChartLabControls({
      chartId: selectedChart.id,
      option: baseOption,
      values: selectedControlState,
      reducedMotion: false
    });
  }, [selectedChart, selectedControlState]);

  function selectChart(chartId: string) {
    setSelectedId(chartId);
    setRecentIds((current) => [chartId, ...current.filter((item) => item !== chartId)].slice(0, 6));
  }

  function updateControl(controlId: string, value: LabChartControlValue) {
    setControlStateByChart((current) => ({
      ...current,
      [selectedChart.id]: {
        ...getDefaultControlState(selectedChart.id),
        ...(current[selectedChart.id] ?? {}),
        [controlId]: value
      }
    }));
  }

  function resetCurrentChart() {
    setControlStateByChart((current) => ({ ...current, [selectedChart.id]: getDefaultControlState(selectedChart.id) }));
  }

  function resetAllCharts() {
    setControlStateByChart({});
  }

  async function copyConfig() {
    const payload = chartConfigPayload({
      chart: selectedChart,
      controls: selectedControlState,
      density,
      size,
      frame,
      publicSafe,
      deploymentMode
    });
    try {
      await navigator.clipboard.writeText(summarizeJson(payload));
      setCopyStatus("copied");
    } catch {
      setCopyStatus("copy failed");
    }
  }

  async function copyPromotionManifest() {
    try {
      await navigator.clipboard.writeText(summarizeJson(selectedPromotion));
      setCopyStatus("promotion copied");
    } catch {
      setCopyStatus("copy failed");
    }
  }

  function togglePinned(chartId: string) {
    setPinnedIds((current) => (current.includes(chartId) ? current.filter((item) => item !== chartId) : [chartId, ...current].slice(0, 8)));
  }

  return (
    <main className="chart-lab" data-density={density} data-theme={themeMode} data-frame={frame} data-capture="false">
      <div className="chart-lab__background" aria-hidden="true" />
      <section className="chart-lab__chrome" aria-label="PRISMA Chart Lab">
        <header className="chart-lab__header">
          <div>
            <span className="eyebrow">PRISMA Chart Lab · {publicSafe ? "public-safe preview" : "local port 3000"}</span>
            <h1>Canonical chart workshop and promotion factory</h1>
          </div>
          <div className="header-actions" aria-label="Lab state">
            <span>{chartOpsChartIds.length} ChartOps</span>
            <span>{workingCount} working</span>
            <span>{placeholderCount} template</span>
            <span>{deploymentMode}</span>
            <span>mock/demo</span>
          </div>
        </header>

        <section className="status-strip" aria-label="Readiness summary">
          <article>
            <span>Lab Health</span>
            <strong>Running locally</strong>
            <small>Port 3000 is the canonical workshop origin.</small>
          </article>
          <article>
            <span>Registry Health</span>
            <strong>{chartOpsChartIds.length} governed charts</strong>
            <small>Atlas, passports, maps, recipes, and states are registry-driven.</small>
          </article>
          <article>
            <span>ECharts Boundary</span>
            <strong>Lab/shared only</strong>
            <small>Product apps do not import the Lab shell.</small>
          </article>
          <article>
            <span>Cloudflare</span>
            <strong>{publicSafe ? "Public-safe" : "Local mode"}</strong>
            <small>Pages export and tunnel docs use isolated preview origins.</small>
          </article>
        </section>

        <section className="lab-workbench">
          <aside className="lab-sidebar" aria-label="Chart navigation">
            <div className="control-card">
              <label>
                <span>Search</span>
                <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="chartId, title, question" />
              </label>
              <label>
                <span>Surface</span>
                <select value={surface} onChange={(event) => setSurface(event.target.value as SurfaceFilter)}>
                  {chartLabSurfaces.map((item) => (
                    <option value={item} key={item}>
                      {item === "all" ? "All surfaces" : item}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Family</span>
                <select value={family} onChange={(event) => setFamily(event.target.value as FamilyFilter)}>
                  {chartLabFamilies.map((item) => (
                    <option value={item} key={item}>
                      {item === "all" ? "All families" : item}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Readiness</span>
                <select value={readiness} onChange={(event) => setReadiness(event.target.value as ReadinessFilter)}>
                  {(["all", "working", "placeholder", "unavailable"] as const).map((item) => (
                    <option value={item} key={item}>{item}</option>
                  ))}
                </select>
              </label>
              <label>
                <span>Minimum confidence {minimumConfidence}%</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={minimumConfidence}
                  onChange={(event) => setMinimumConfidence(Number(event.target.value))}
                />
              </label>
            </div>

            <div className="mini-stack">
              <span className="eyebrow">Pinned</span>
              <p>{pinnedIds.length ? pinnedIds.join(", ") : "No pinned charts."}</p>
              <span className="eyebrow">Recent</span>
              <p>{recentIds.length ? recentIds.join(", ") : "No recent charts."}</p>
            </div>

            <nav className="chart-list" aria-label="Registered charts">
              {filteredCharts.map((chart) => (
                <button
                  type="button"
                  key={chart.id}
                  className={chart.id === selectedChart.id ? "chart-list__item is-active" : "chart-list__item"}
                  onClick={() => selectChart(chart.id)}
                  aria-pressed={chart.id === selectedChart.id}
                >
                  <span className={`readiness-dot readiness-dot--${readinessTone(chart.readiness)}`} />
                  <span>
                    <strong>{chart.title}</strong>
                    <small>{surfaceLabel(chart.surface)} · {chart.family}</small>
                  </span>
                </button>
              ))}
            </nav>
          </aside>

          <section className="preview-stage" aria-label="Chart preview">
            <div className="preview-toolbar">
              <div>
                <span className="eyebrow">{selectedChart.id}</span>
                <h2>{selectedChart.title}</h2>
              </div>
              <div className="segmented-controls" aria-label="Visual controls">
                <button type="button" className={themeMode === "prisma-crystal" ? "is-active" : ""} onClick={() => setThemeMode("prisma-crystal")}>
                  Crystal
                </button>
                <button type="button" className={themeMode === "precision-paper" ? "is-active" : ""} onClick={() => setThemeMode("precision-paper")}>
                  Paper
                </button>
                <button type="button" className={density === "calm" ? "is-active" : ""} onClick={() => setDensity("calm")}>
                  Calm
                </button>
                <button type="button" className={density === "dense" ? "is-active" : ""} onClick={() => setDensity("dense")}>
                  Dense
                </button>
              </div>
            </div>

            <div className="size-controls" aria-label="Chart size controls">
              {(["focus", "wide", "compact"] as const).map((item) => (
                <button type="button" key={item} className={size === item ? "is-active" : ""} onClick={() => setSize(item)}>
                  {item}
                </button>
              ))}
              {(["pc", "tablet", "mobile"] as const).map((item) => (
                <button type="button" key={item} className={frame === item ? "is-active" : ""} onClick={() => setFrame(item)}>
                  {item}
                </button>
              ))}
              <button type="button" className={pinnedIds.includes(selectedChart.id) ? "is-active" : ""} onClick={() => togglePinned(selectedChart.id)}>
                Pin
              </button>
            </div>

            <article className="chart-frame" data-preview-frame={frame}>
              {selectedChart.Component ? (
                <selectedChart.Component entry={selectedChart} density={density} size={size} themeMode={themeMode} />
              ) : (
                <LabEChartFrame entry={selectedChart} density={density} size={size} optionOverride={optionOverride} />
              )}
            </article>

            <div className="tab-strip" role="tablist" aria-label="Chart inspector tabs">
              {inspectorTabs.map((item) => (
                <button type="button" role="tab" key={item.id} aria-selected={tab === item.id} className={tab === item.id ? "is-active" : ""} onClick={() => setTab(item.id)}>
                  {item.label}
                </button>
              ))}
            </div>

            {tab === "controls" ? (
              <ChartControlDeck
                controls={selectedControls}
                values={selectedControlState}
                onChange={updateControl}
                onCopyConfig={copyConfig}
                onReset={resetCurrentChart}
                onResetAll={resetAllCharts}
              />
            ) : null}

            {tab !== "controls" ? (
              <section className="tab-panel" aria-label={`${tab} panel`}>
                {tab === "preview" ? (
                  <div className="panel-grid">
                    <article>
                      <span className="eyebrow">Control Summary</span>
                      <dl>
                        <div><dt>Chart</dt><dd>{selectedChart.id}</dd></div>
                        <div><dt>Surface</dt><dd>{selectedChart.surface}</dd></div>
                        <div><dt>Active controls</dt><dd>{activeControls}</dd></div>
                        <div><dt>Data scenario</dt><dd>{String(selectedControlState.dataScenario ?? "clean")}</dd></div>
                        <div><dt>Visual recipe</dt><dd>{selectedPassport?.visualRecipe ?? `${selectedChart.family}Recipe`}</dd></div>
                        <div><dt>Timestamp</dt><dd>{new Date().toISOString()}</dd></div>
                      </dl>
                      <div className="toolbar-actions">
                        <button type="button" onClick={copyConfig}>Copy Current Config JSON</button>
                        <button type="button" onClick={resetCurrentChart}>Reset current chart</button>
                      </div>
                      <small>{copyStatus}</small>
                    </article>
                    <article>
                      <span className="eyebrow">Question</span>
                      <p>{selectedChart.operationalQuestion}</p>
                      <span className="eyebrow">Promotion Boundary</span>
                      <p>{selectedChart.promotionBoundary}</p>
                    </article>
                  </div>
                ) : null}

                {tab === "passport" ? (
                  <pre>{summarizeJson(selectedPassport)}</pre>
                ) : null}

                {tab === "maps" ? (
                  <div className="map-stack">
                    <pre>{summarizeJson({
                      atlas: chartLabMapCatalog.chartAtlasMap.find((item) => item.chartId === selectedChart.id),
                      controls: chartLabMapCatalog.runtimeControlMap.find((item) => item.chartId === selectedChart.id),
                      knobs: chartLabMapCatalog.visualKnobMap.find((item) => item.chartId === selectedChart.id),
                      routes: selectedRoute,
                      validation: validationMap
                    })}</pre>
                  </div>
                ) : null}

                {tab === "data" ? (
                  <pre>{summarizeJson(selectedDataSource)}</pre>
                ) : null}

                {tab === "promotion" ? (
                  <div className="map-stack">
                    <pre>{summarizeJson({ transport: selectedTransport, promotion: selectedPromotion })}</pre>
                    <div className="toolbar-actions">
                      <button type="button" onClick={copyPromotionManifest}>Copy Promotion Manifest JSON</button>
                    </div>
                  </div>
                ) : null}

                {tab === "intent" ? (
                  <pre>{summarizeJson(humanIntentMap)}</pre>
                ) : null}

                {tab === "states" ? (
                  <pre>{summarizeJson(selectedStates)}</pre>
                ) : null}

                {tab === "health" ? (
                  <div className="panel-grid">
                    {asArray([
                      ["Lab Health", "PASS", "Local 3000 workshop, static export capable."],
                      ["Registry Health", "PASS", `${chartOpsChartIds.length} ChartOps charts plus future placeholder.`],
                      ["ECharts Boundary", "PASS", "ECharts stays in Lab/shared renderer boundary."],
                      ["Cloudflare Health", "CONFIGURED", "Pages/tunnel scripts exist; auth decides live deployment."],
                      ["Tunnel Health", "DOCTOR", "cloudflared doctor checks install, token/config, and port 3000."],
                      ["Chart 15 Walkthrough", "READY", "Use NEW_CHART_TEMPLATE.md plus scaffold:chart and verifier chain."]
                    ]).map(([label, status, note]) => (
                      <article key={label}>
                        <span className="eyebrow">{label}</span>
                        <strong>{status}</strong>
                        <p>{note}</p>
                      </article>
                    ))}
                  </div>
                ) : null}
              </section>
            ) : null}
          </section>

          <aside className="inspector" aria-label="Chart readiness inspector">
            <section>
              <span className="eyebrow">Snapshot</span>
              <dl>
                <div>
                  <dt>Readiness</dt>
                  <dd>{selectedChart.readiness}</dd>
                </div>
                <div>
                  <dt>Data status</dt>
                  <dd>{selectedChart.dataStatus}</dd>
                </div>
                <div>
                  <dt>Confidence</dt>
                  <dd>{selectedChart.confidence}%</dd>
                </div>
                <div>
                  <dt>Freshness</dt>
                  <dd>{selectedChart.freshnessLabel}</dd>
                </div>
              </dl>
            </section>

            <section>
              <span className="eyebrow">Public Safety</span>
              <p>{publicSafe ? "Public-safe mode is active. Local paths and private diagnostics are hidden." : "Local mode. Cloudflare builds force public-safe mode."}</p>
              <small>Data is mock/demo unless a surface adapter explicitly marks it otherwise.</small>
            </section>

            <section>
              <span className="eyebrow">Transport</span>
              <p>{selectedTransport?.surfaceProfile}</p>
              <small>Feature flag: {selectedTransport?.requiredFeatureFlag}</small>
            </section>

            {!publicSafe ? (
              <section>
                <span className="eyebrow">Files</span>
                <code>{selectedChart.componentPath}</code>
                <code>{selectedChart.mockPath}</code>
                <code>{selectedChart.registryPath}</code>
              </section>
            ) : null}
          </aside>
        </section>
      </section>
    </main>
  );
}
