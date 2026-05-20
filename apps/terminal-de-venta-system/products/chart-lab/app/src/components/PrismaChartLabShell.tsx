// PRISMA_PEARL_EXECUTIVE_LUXURY_SHELL_V1
"use client";

import { useMemo, useState, useEffect } from "react";
import { ChartControlDeck } from "@/components/ChartControlDeck";
import { OptionStudioPanel } from "@/components/OptionStudioPanel";
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
  LabChartRuntimeControl,
  LabChartSize,
  LabChartThemeMode
} from "@/prisma-charts/chart-lab-types";


function HydrationSafeTimestamp() {
  const [timestamp, setTimestamp] = useState("pending");

  useEffect(() => {
    setTimestamp(new Date().toISOString());
  }, []);

  return <>{timestamp}</>;
}


type SurfaceFilter = (typeof chartLabSurfaces)[number];
type FamilyFilter = (typeof chartLabFamilies)[number];
type ReadinessFilter = "all" | LabChartEntry["readiness"];

const inspectorTabs: Array<{ id: LabChartInspectorTab; label: string }> = [
  { id: "preview", label: "Preview" },
  { id: "controls", label: "Controls" },
  { id: "option-studio", label: "Option Studio" },
  { id: "passport", label: "Passport" },
  { id: "maps", label: "Maps" },
  { id: "data", label: "Sources" },
  { id: "promotion", label: "Promotion" },
  { id: "intent", label: "Intent" },
  { id: "states", label: "States" },
  { id: "health", label: "Health" }
];

function initialSearchParam(name: string) {
  if (typeof window === "undefined") return null;
  return new URLSearchParams(window.location.search).get(name);
}

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


const HEATMAP_CHART_ID = "ops.operational-density-heatmap";

const heatmapRuntimeControls: LabChartRuntimeControl[] = [
  {
    id: "heatPalette",
    label: "Heat palette",
    type: "segmented",
    defaultValue: "control-spectrum",
    options: [
      { label: "Controls", value: "control-spectrum" },
      { label: "Thermal", value: "thermal" },
      { label: "Aurora", value: "aurora" },
      { label: "Critical", value: "critical" }
    ],
    affectedLayer: "visualMap.inRange.color",
    validation: "Palette only changes visual encoding; source evidence stays intact.",
    risk: "low",
    resetBehavior: "Returns to PRISMA control-spectrum palette."
  },
  {
    id: "heatZoneMode",
    label: "Heat zones",
    type: "segmented",
    defaultValue: "balanced",
    options: [
      { label: "Balanced", value: "balanced" },
      { label: "Gateway noon", value: "gateway-noon" },
      { label: "Payments night", value: "payments-night" },
      { label: "Ops wave", value: "ops-wave" },
      { label: "Stress demo", value: "stress-demo" }
    ],
    affectedLayer: "series[0].data.value[2]",
    validation: "Lab-only deterministic transform for exploring hot-zone storytelling.",
    risk: "low",
    resetBehavior: "Balanced distribution with two evidence callouts."
  },
  {
    id: "heatIntensity",
    label: "Heat intensity",
    type: "range",
    defaultValue: 112,
    min: 70,
    max: 150,
    step: 2,
    affectedLayer: "series[0].data.value[2]",
    validation: "Scales pressure values for visual stress testing without touching source adapters.",
    risk: "low",
    resetBehavior: "112"
  },
  {
    id: "hotspotBias",
    label: "Hotspot bias",
    type: "range",
    defaultValue: 18,
    min: 0,
    max: 42,
    step: 1,
    affectedLayer: "series[0].data.value[2]",
    validation: "Adds localized heat near the chosen operational zone.",
    risk: "low",
    resetBehavior: "18"
  },
  {
    id: "heatCeiling",
    label: "Heat ceiling",
    type: "range",
    defaultValue: 90,
    min: 72,
    max: 100,
    step: 1,
    affectedLayer: "visualMap.max",
    validation: "Lower ceilings reveal yellow/red cells faster; higher ceilings make palette calmer.",
    risk: "low",
    resetBehavior: "90"
  },
  {
    id: "gridVisibility",
    label: "Cell grid",
    type: "range",
    defaultValue: 18,
    min: 0,
    max: 55,
    step: 1,
    affectedLayer: "series[0].itemStyle.borderColor",
    validation: "Keeps the square-cell texture visible without turning it into a spreadsheet.",
    risk: "low",
    resetBehavior: "18"
  },
  {
    id: "showCellNumbers",
    label: "Cell numbers",
    type: "toggle",
    defaultValue: false,
    affectedLayer: "series[0].label.show",
    validation: "Off by default because numbers flatten the thermal field into a table.",
    risk: "low",
    resetBehavior: "Disabled"
  },
  {
    id: "showCallouts",
    label: "Callouts",
    type: "toggle",
    defaultValue: true,
    affectedLayer: "graphic[].invisible",
    validation: "Keeps executive annotations optional and non-destructive.",
    risk: "low",
    resetBehavior: "Enabled"
  },
  {
    id: "motionMode",
    label: "Motion",
    type: "segmented",
    defaultValue: "sweep",
    options: [
      { label: "Still", value: "still" },
      { label: "Sweep", value: "sweep" },
      { label: "Pulse", value: "pulse" }
    ],
    affectedLayer: "animation + CSS frame aura",
    validation: "Cosmetic chart-lab motion only; respects exported static data.",
    risk: "low",
    resetBehavior: "Sweep"
  }
];

const heatmapDefaultControlState: LabChartControlState = Object.fromEntries(
  heatmapRuntimeControls.map((control) => [control.id, control.defaultValue])
) as LabChartControlState;

function getChartDefaultControlState(chartId: string): LabChartControlState {
  return {
    ...getDefaultControlState(chartId),
    ...(chartId === HEATMAP_CHART_ID ? heatmapDefaultControlState : {})
  };
}

function getControlsForLabChart(chartId: string) {
  const controls = getControlsForChart(chartId);
  if (chartId !== HEATMAP_CHART_ID) return controls;
  const existingIds = new Set(controls.map((control) => control.id));
  return [...controls, ...heatmapRuntimeControls.filter((control) => !existingIds.has(control.id))];
}

function countLabChartActiveControls(chartId: string, values: LabChartControlState) {
  return getControlsForLabChart(chartId).filter((control) => JSON.stringify(values[control.id] ?? control.defaultValue) !== JSON.stringify(control.defaultValue)).length;
}

function numericControl(values: LabChartControlState, id: string, fallback: number) {
  const value = values[id];
  return typeof value === "number" ? value : fallback;
}

function stringControl(values: LabChartControlState, id: string, fallback: string) {
  const value = values[id];
  return typeof value === "string" ? value : fallback;
}

function booleanControl(values: LabChartControlState, id: string, fallback: boolean) {
  const value = values[id];
  return typeof value === "boolean" ? value : fallback;
}

function heatmapPalette(value: string) {
  if (value === "thermal") return ["#06111f", "#103579", "#1769ff", "#18d7ff", "#7f5cff", "#f250b7", "#ff516d", "#ff9d42", "#fff0a6"];
  if (value === "aurora") return ["#051229", "#083163", "#0d69cd", "#18e4ff", "#3cffd0", "#8d5cff", "#e747ff", "#ff7fc7", "#fff2b8"];
  if (value === "critical") return ["#061229", "#0d2f75", "#136ee4", "#16d4ff", "#705cff", "#d847e8", "#ff3366", "#ff7b35", "#ffe98f"];
  return ["#051229", "#0b2e72", "#1167dd", "#18d7ff", "#735cff", "#e44bc2", "#ff536d", "#ff9f4d", "#fff0a8"];
}

function bucketHour(label: unknown) {
  if (typeof label !== "string") return 0;
  const [hour, minute] = label.split(":").map((part) => Number(part));
  return (Number.isFinite(hour) ? hour : 0) + (Number.isFinite(minute) ? minute / 60 : 0);
}

function zoneInfluence(zone: string, moduleName: string, hour: number) {
  if (zone === "gateway-noon") {
    const moduleBoost = moduleName === "API Gateway" ? 1 : moduleName === "Plataforma Web" || moduleName === "Autenticación" ? 0.62 : 0.18;
    return Math.exp(-Math.pow(hour - 12.55, 2) / 1.25) * moduleBoost;
  }
  if (zone === "payments-night") {
    const moduleBoost = moduleName === "Pagos" ? 1 : moduleName === "Integraciones" || moduleName === "Data Pipeline" ? 0.72 : 0.16;
    return Math.exp(-Math.pow(hour - 19.55, 2) / 1.35) * moduleBoost;
  }
  if (zone === "ops-wave") {
    const bandCenter = moduleName === "Reportes" || moduleName === "Notificaciones" ? 10.5 : moduleName === "Órdenes" || moduleName === "Inventario" ? 13.2 : 16.5;
    return Math.exp(-Math.pow(hour - bandCenter, 2) / 4.8) * 0.78;
  }
  if (zone === "stress-demo") {
    const noon = Math.exp(-Math.pow(hour - 12.4, 2) / 2.2);
    const night = Math.exp(-Math.pow(hour - 19.4, 2) / 2.0);
    return Math.max(noon, night) * 0.92;
  }
  return 0.34 * Math.exp(-Math.pow(hour - 12.35, 2) / 7.2);
}

function applyOperationalDensityHeatmapControls(option: Record<string, unknown>, values: LabChartControlState): Record<string, unknown> {
  const palette = heatmapPalette(stringControl(values, "heatPalette", "control-spectrum"));
  const zoneMode = stringControl(values, "heatZoneMode", "balanced");
  const intensity = numericControl(values, "heatIntensity", 112) / 100;
  const hotspotBias = numericControl(values, "hotspotBias", 18);
  const heatCeiling = numericControl(values, "heatCeiling", 90);
  const gridVisibility = numericControl(values, "gridVisibility", 18);
  const showCellNumbers = booleanControl(values, "showCellNumbers", false);
  const showCallouts = booleanControl(values, "showCallouts", true);
  const motionMode = stringControl(values, "motionMode", "sweep");
  const cloned: Record<string, unknown> = { ...option };

  cloned.animation = motionMode !== "still";
  cloned.animationDurationUpdate = motionMode === "pulse" ? 980 : motionMode === "sweep" ? 720 : 0;
  cloned.animationEasingUpdate = motionMode === "pulse" ? "elasticOut" : "quarticOut";

  const visualMapArray = Array.isArray(cloned.visualMap) ? cloned.visualMap : cloned.visualMap ? [cloned.visualMap] : [];
  cloned.visualMap = visualMapArray.map((visualMap) => ({
    ...(visualMap as Record<string, unknown>),
    max: heatCeiling,
    inRange: { ...((visualMap as Record<string, unknown>).inRange as Record<string, unknown> | undefined), color: palette }
  }));

  if (!visualMapArray.length) {
    cloned.visualMap = [{
      show: false,
      type: "continuous",
      min: 0,
      max: heatCeiling,
      dimension: 2,
      seriesIndex: 0,
      inRange: { color: palette }
    }];
  }

  const borderAlpha = Math.max(0, Math.min(0.55, gridVisibility / 100));
  const seriesArray = Array.isArray(cloned.series) ? cloned.series : [];
  cloned.series = seriesArray.map((series) => {
    const seriesRecord = series as Record<string, unknown>;
    if (seriesRecord.type !== "heatmap") return seriesRecord;

    const nextData = Array.isArray(seriesRecord.data)
      ? seriesRecord.data.map((cell) => {
          const cellRecord = cell as Record<string, unknown>;
          const value = Array.isArray(cellRecord.value) ? [...cellRecord.value] : [];
          const meta = cellRecord.meta as Record<string, unknown> | undefined;
          const moduleName = String(meta?.moduleName ?? "");
          const label = meta?.bucketLabel ?? value[0];
          const hour = bucketHour(label);
          const rawScore = typeof value[2] === "number" ? value[2] : Number(value[2] ?? 0);
          const boostedScore = Math.max(0, Math.min(100, Math.round((rawScore * intensity) + zoneInfluence(zoneMode, moduleName, hour) * hotspotBias)));
          value[2] = boostedScore;
          const nextMeta = meta ? {
            ...meta,
            pressureScore: boostedScore,
            warnCount: boostedScore > 68 ? Math.max(Number(meta.warnCount ?? 0), 2) : meta.warnCount,
            errorCount: boostedScore > 88 ? Math.max(Number(meta.errorCount ?? 0), 1) : meta.errorCount,
            dominantCause: boostedScore > 88 ? "runtime_heat_zone" : meta.dominantCause
          } : meta;

          return {
            ...cellRecord,
            value,
            meta: nextMeta,
            label: { show: showCellNumbers, formatter: showCellNumbers ? "{@[2]}" : "" },
            itemStyle: {
              ...((cellRecord.itemStyle as Record<string, unknown> | undefined) ?? {}),
              borderColor: `rgba(168, 220, 255, ${borderAlpha.toFixed(2)})`,
              borderWidth: gridVisibility > 0 ? Math.max(0.2, gridVisibility / 45) : 0
            }
          };
        })
      : seriesRecord.data;

    return {
      ...seriesRecord,
      data: nextData,
      label: { show: showCellNumbers, formatter: showCellNumbers ? (params: any) => `${params.data?.value?.[2] ?? ""}` : "" },
      itemStyle: {
        ...((seriesRecord.itemStyle as Record<string, unknown> | undefined) ?? {}),
        borderColor: `rgba(168, 220, 255, ${borderAlpha.toFixed(2)})`,
        borderWidth: gridVisibility > 0 ? Math.max(0.2, gridVisibility / 45) : 0,
        shadowBlur: motionMode === "pulse" ? 8 : 2,
        shadowColor: motionMode === "pulse" ? "rgba(255, 83, 109, 0.18)" : "rgba(31, 231, 255, 0.08)"
      },
      emphasis: {
        ...((seriesRecord.emphasis as Record<string, unknown> | undefined) ?? {}),
        label: { show: false },
        itemStyle: {
          ...(((seriesRecord.emphasis as Record<string, unknown> | undefined)?.itemStyle as Record<string, unknown> | undefined) ?? {}),
          borderColor: "rgba(255,255,255,.86)",
          borderWidth: 1.05,
          shadowBlur: 16
        }
      },
      blur: { label: { show: false } },
      select: { label: { show: false } }
    };
  });

  const graphicArray = Array.isArray(cloned.graphic) ? cloned.graphic : cloned.graphic ? [cloned.graphic] : [];
  cloned.graphic = graphicArray.map((graphic) => ({ ...(graphic as Record<string, unknown>), invisible: !showCallouts }));

  return cloned;
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

// PRISMA_CAUSAL_FLOW_PREMIUM_PATCH_V2: Causal Flow Ribbon hero evidence strip.
// PRISMA_KNOBS_AUDIT_INJECTION_V2: selected chart/tab metadata for code-first audits.

function cloneOptionStudioPreview(option: Record<string, unknown>): Record<string, unknown> {
  return JSON.parse(JSON.stringify(option)) as Record<string, unknown>;
}

export function PrismaChartLabShell() {
  const publicSafe = process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE === "true";
  const deploymentMode = process.env.NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE ?? "local";
  const [selectedId, setSelectedId] = useState(() => initialSearchParam("chart") ?? chartLabRegistry[0]?.id ?? "");
  const [surface, setSurface] = useState<SurfaceFilter>("all");
  const [family, setFamily] = useState<FamilyFilter>("all");
  const [readiness, setReadiness] = useState<ReadinessFilter>("all");
  const [search, setSearch] = useState("");
  const [themeMode, setThemeMode] = useState<LabChartThemeMode>("prisma-crystal");
  const [density, setDensity] = useState<LabChartDensity>("calm");
  const [size, setSize] = useState<LabChartSize>("focus");
  const [frame, setFrame] = useState<LabChartPreviewFrame>(() => {
    const value = initialSearchParam("frame");
    return value === "tablet" || value === "mobile" || value === "pc" ? value : "pc";
  });
  const [minimumConfidence, setMinimumConfidence] = useState(0);
  const [tab, setTab] = useState<LabChartInspectorTab>(() => {
    const value = initialSearchParam("tab");
    return inspectorTabs.find((item) => item.id === value)?.id ?? "preview";
  });
  const [pinnedIds, setPinnedIds] = useState<string[]>([]);
  const [recentIds, setRecentIds] = useState<string[]>([]);
  const [controlStateByChart, setControlStateByChart] = useState<Record<string, LabChartControlState>>({});
  const [optionStudioOverrideByChart, setOptionStudioOverrideByChart] = useState<Record<string, Record<string, unknown>>>({});
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
  const selectedControls = getControlsForLabChart(selectedChart.id);
  const selectedControlState = { ...getChartDefaultControlState(selectedChart.id), ...(controlStateByChart[selectedChart.id] ?? {}) };
  const workingCount = chartLabRegistry.filter((chart) => chart.readiness === "working").length;
  const placeholderCount = chartLabRegistry.filter((chart) => chart.readiness === "placeholder").length;
  const activeControls = selectedChart.id === HEATMAP_CHART_ID ? countLabChartActiveControls(selectedChart.id, selectedControlState) : countActiveControls(selectedChart.id, selectedControlState);
  const selectedPassport = visualTuningPassports.find((item) => item.chartId === selectedChart.id);
  const selectedDataSource = dataSourceMap.find((item) => item.chartId === selectedChart.id);
  const selectedTransport = surfaceTransportMap.find((item) => item.chartId === selectedChart.id);
  const selectedPromotion = promotionManifestMap.find((item) => item.chartId === selectedChart.id);
  const selectedRoute = routeMap.find((item) => item.chartId === selectedChart.id);
  const selectedStates = stateGalleryMap.find((item) => item.chartId === selectedChart.id);

  const optionOverride = useMemo(() => {
    const baseOption = selectedChart.getOption?.();
    if (!baseOption) return undefined;
    const controlledOption = applyChartLabControls({
      chartId: selectedChart.id,
      option: baseOption,
      values: selectedControlState,
      reducedMotion: false
    });
    return selectedChart.id === HEATMAP_CHART_ID
      ? applyOperationalDensityHeatmapControls(controlledOption, selectedControlState)
      : controlledOption;
  }, [selectedChart, selectedControlState]);
  const optionStudioOverride = optionStudioOverrideByChart[selectedChart.id];
  const previewOptionOverride = useMemo(() => {
    if (!optionStudioOverride) return optionOverride;
    const controlledStudioOption = applyChartLabControls({
      chartId: selectedChart.id,
      option: cloneOptionStudioPreview(optionStudioOverride),
      values: selectedControlState,
      reducedMotion: false
    });
    return selectedChart.id === HEATMAP_CHART_ID
      ? applyOperationalDensityHeatmapControls(controlledStudioOption, selectedControlState)
      : controlledStudioOption;
  }, [optionOverride, optionStudioOverride, selectedChart.id, selectedControlState]);

  function selectChart(chartId: string) {
    setSelectedId(chartId);
    setRecentIds((current) => [chartId, ...current.filter((item) => item !== chartId)].slice(0, 6));
  }

  function updateControl(controlId: string, value: LabChartControlValue) {
    setControlStateByChart((current) => ({
      ...current,
      [selectedChart.id]: {
        ...getChartDefaultControlState(selectedChart.id),
        ...(current[selectedChart.id] ?? {}),
        [controlId]: value
      }
    }));
  }

  function resetCurrentChart() {
    setControlStateByChart((current) => ({ ...current, [selectedChart.id]: getChartDefaultControlState(selectedChart.id) }));
  }

  function applyOptionStudioPreview(option: Record<string, unknown>) {
    setOptionStudioOverrideByChart((current) => ({ ...current, [selectedChart.id]: option }));
  }

  function resetOptionStudioPreview() {
    setOptionStudioOverrideByChart((current) => {
      const next = { ...current };
      delete next[selectedChart.id];
      return next;
    });
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
    <main className="chart-lab" data-luxury-ui="pearl-executive" data-density={density} data-theme={themeMode} data-frame={frame} data-capture="false" data-selected-chart-id={selectedChart.id} data-selected-tab={tab} data-active-controls={activeControls}>
      <div className="chart-lab__background" aria-hidden="true" />
      <section className="chart-lab__chrome" aria-label="PRISMA Chart Lab">
        <header className="chart-lab__header">
          {/* PRISMA_CHART_LAB_BRAND_LOGO_V1 */}
          <div className="prisma-brand-lockup" aria-label="PRISMA Chart Lab brand" data-prisma-brand-logo="true">
            <img className="prisma-brand-lockup__mark" src="/brand/prisma-prism-mark.png" alt="" aria-hidden="true" loading="eager" decoding="async" />
            <div className="prisma-brand-lockup__copy">
              <span className="eyebrow">PRISMA Pearl Executive · {publicSafe ? "public-safe preview" : "local atelier"}</span>
              <h1>PRISMA Chart Lab</h1>
              <p className="prisma-brand-lockup__tagline">Governed visual intelligence for audit-ready operational charts.</p>
            </div>
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
                  data-chart-id={chart.id}
                  data-chart-title={chart.title}
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

            <article className="chart-frame" data-preview-frame={frame} data-chart-id={selectedChart.id} data-chart-family={selectedChart.family} data-active-controls={activeControls} data-heat-palette={selectedChart.id === HEATMAP_CHART_ID ? String(selectedControlState.heatPalette ?? "control-spectrum") : undefined} data-heat-zone={selectedChart.id === HEATMAP_CHART_ID ? String(selectedControlState.heatZoneMode ?? "balanced") : undefined} data-heat-motion={selectedChart.id === HEATMAP_CHART_ID ? String(selectedControlState.motionMode ?? "sweep") : undefined}>
              {selectedChart.id === "pc.causal-flow-ribbon" ? (
                <div className="causal-hero-strip" aria-label="Causal Flow Ribbon evidence summary">
                  <div>
                    <span className="eyebrow">Causal command ribbon</span>
                    <strong>{String(selectedControlState.detailLevel ?? "standard")} · {String(selectedControlState.dataScenario ?? "clean")}</strong>
                  </div>
                  <div className="causal-hero-strip__chips">
                    <span>confidence ≥ {String(selectedControlState.confidenceFloor ?? 0)}%</span>
                    <span>stage {String(selectedControlState.stageFocus ?? "all")}</span>
                    <span>evidence {String(selectedControlState.evidenceMode ?? true)}</span>
                    <span>{activeControls} active knobs</span>
                  </div>
                </div>
              ) : null}

              {selectedChart.id === "ops.operational-density-heatmap" ? (
                <div className="density-hero-strip" aria-label="Operational Density Heatmap evidence summary">
                  <div>
                    <span className="eyebrow">Operational density matrix</span>
                    <strong>10 modules · 49 half-hour cells · thermal density matrix</strong>
                  </div>
                  <div className="density-hero-strip__chips">
                    <span>{String(selectedControlState.heatPalette ?? "control-spectrum")}</span>
                    <span>{String(selectedControlState.heatZoneMode ?? "balanced")}</span>
                    <span>intensity {String(selectedControlState.heatIntensity ?? 112)}</span>
                    <span>{activeControls} active knobs</span>
                  </div>
                </div>
              ) : null}
              {selectedChart.Component ? (
                <selectedChart.Component entry={selectedChart} density={density} size={size} themeMode={themeMode} />
              ) : (
                <LabEChartFrame entry={selectedChart} density={density} size={size} optionOverride={previewOptionOverride} />
              )}
              {selectedChart.id === "ops.operational-density-heatmap" ? (
                <div className="density-matrix-legend" aria-label="Densidad Operacional de baja a alta">
                  <span>Densidad Operacional</span>
                  <i aria-hidden="true" />
                  <small>Baja</small>
                  <small>Alta</small>
                </div>
              ) : null}
            </article>

            <div className="tab-strip" role="tablist" aria-label="Chart inspector tabs">
              {inspectorTabs.map((item) => (
                <button type="button" role="tab" key={item.id} data-tab-id={item.id} aria-selected={tab === item.id} className={tab === item.id ? "is-active" : ""} onClick={() => setTab(item.id)}>
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
                        <div><dt>Timestamp</dt><dd><HydrationSafeTimestamp /></dd></div>
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

                {tab === "option-studio" ? (
                  <OptionStudioPanel
                    chart={selectedChart}
                    canonicalOption={optionOverride}
                    previewOption={previewOptionOverride}
                    hasPreviewOverride={Boolean(optionStudioOverride)}
                    onApplyPreview={applyOptionStudioPreview}
                    onResetPreview={resetOptionStudioPreview}
                  />
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
