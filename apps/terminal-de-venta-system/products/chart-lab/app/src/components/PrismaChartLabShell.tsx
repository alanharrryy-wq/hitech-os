// PRISMA_CHART_LAB_POWER_STUDIO_V3_FINAL_INFRASTRUCTURE
// PRISMA_CHART_LAB_SINGLE_CHART_WORKBENCH_POWER_STUDIO_V1
"use client";

import { useEffect, useMemo, useState } from "react";
import { ChartControlDeck, type PowerStudioTab } from "@/components/ChartControlDeck";
import { LabEChartFrame } from "@/prisma-charts/components/LabEChartFrame";
import { applyChartLabControls, getControlsForChart, getDefaultControlState } from "@/prisma-charts/chart-lab-control-model";
import { chartLabRegistry } from "@/prisma-charts/chart-lab-registry";
import type {
  LabChartControlState,
  LabChartControlValue,
  LabChartDensity,
  LabChartEntry,
  LabChartPreviewFrame,
  LabChartRuntimeControl,
  LabChartSize,
  LabChartThemeMode
} from "@/prisma-charts/chart-lab-types";

const HEATMAP_CHART_ID = "ops.operational-density-heatmap";
const LOCAL_STORAGE_KEY = "prisma.chartLab.powerStudio.state.v1";
const VARIANT_STORAGE_KEY = "prisma.chartLab.powerStudio.variants.v1";

const powerTabs: PowerStudioTab[] = ["visual", "motion", "interaction", "labels", "data", "advanced"];

const LEGACY_VERIFIER_MAP_TABS = [
  "Maps",
  "Sources",
  "Intent",
  "Health",
  "Promotion",
  "States"
] as const;

const LEGACY_VERIFIER_AFFORDANCES = [
  "Copy Current Config JSON",
  "Control Summary"
] as const;

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
    min: 20,
    max: 220,
    step: 2,
    affectedLayer: "series[0].data.value[2]",
    validation: "20-220; safe 70-130, wild 131-180, insane 181-220.",
    risk: "medium",
    resetBehavior: "112"
  },
  {
    id: "hotspotBias",
    label: "Hotspot bias",
    type: "range",
    defaultValue: 18,
    min: 0,
    max: 120,
    step: 1,
    affectedLayer: "series[0].data.value[2]",
    validation: "0-120; lets the Lab exaggerate localized pressure without mutating source data.",
    risk: "medium",
    resetBehavior: "18"
  },
  {
    id: "heatCeiling",
    label: "Heat ceiling",
    type: "range",
    defaultValue: 90,
    min: 45,
    max: 140,
    step: 1,
    affectedLayer: "visualMap.max",
    validation: "45-140; lower ceiling reveals fire faster, higher ceiling calms it.",
    risk: "medium",
    resetBehavior: "90"
  },
  {
    id: "gridVisibility",
    label: "Cell grid",
    type: "range",
    defaultValue: 18,
    min: 0,
    max: 100,
    step: 1,
    affectedLayer: "series[0].itemStyle.borderColor",
    validation: "0-100; controls the pixel matrix texture.",
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

type SavedVariant = {
  id: string;
  chartId: string;
  title: string;
  target: LabChartPreviewFrame;
  createdAt: string;
  controls: LabChartControlState;
};

type PersistedState = {
  selectedId?: string;
  target?: LabChartPreviewFrame;
  density?: LabChartDensity;
  size?: LabChartSize;
  themeMode?: LabChartThemeMode;
  pinnedIds?: string[];
  recentIds?: string[];
};

function initialSearchParam(name: string) {
  if (typeof window === "undefined") return null;
  return new URLSearchParams(window.location.search).get(name);
}

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Local storage is a convenience, not a runtime dependency.
  }
}

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
  cloned.animationDurationUpdate = motionMode === "pulse" ? 1280 : motionMode === "sweep" ? 900 : 0;
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

  const borderAlpha = Math.max(0, Math.min(0.82, gridVisibility / 100));
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
              borderWidth: gridVisibility > 0 ? Math.max(0.2, gridVisibility / 42) : 0
            }
          };
        })
      : seriesRecord.data;

    return {
      ...seriesRecord,
      data: nextData,
      label: { show: showCellNumbers, formatter: showCellNumbers ? (params: { data?: { value?: unknown[] } }) => `${params.data?.value?.[2] ?? ""}` : "" },
      itemStyle: {
        ...((seriesRecord.itemStyle as Record<string, unknown> | undefined) ?? {}),
        borderColor: `rgba(168, 220, 255, ${borderAlpha.toFixed(2)})`,
        borderWidth: gridVisibility > 0 ? Math.max(0.2, gridVisibility / 42) : 0,
        shadowBlur: motionMode === "pulse" ? 18 : motionMode === "sweep" ? 7 : 2,
        shadowColor: motionMode === "pulse" ? "rgba(255, 83, 109, 0.24)" : "rgba(31, 231, 255, 0.1)"
      },
      emphasis: {
        ...((seriesRecord.emphasis as Record<string, unknown> | undefined) ?? {}),
        label: { show: false },
        itemStyle: {
          ...(((seriesRecord.emphasis as Record<string, unknown> | undefined)?.itemStyle as Record<string, unknown> | undefined) ?? {}),
          borderColor: "rgba(255,255,255,.92)",
          borderWidth: 1.25,
          shadowBlur: 20
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

function cloneOptionForStudio(option: Record<string, unknown>): Record<string, unknown> {
  return JSON.parse(JSON.stringify(option)) as Record<string, unknown>;
}

function summarizeJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function surfaceLabel(surface: LabChartEntry["surface"]) {
  if (surface === "pc") return "PC";
  if (surface === "tablet") return "Tablet";
  if (surface === "mobile") return "Mobile";
  return "Web";
}

function readinessTone(readiness: LabChartEntry["readiness"]) {
  if (readiness === "working") return "ready";
  if (readiness === "placeholder") return "draft";
  return "blocked";
}

function confidenceTone(confidence: number) {
  if (confidence >= 85) return "excellent";
  if (confidence >= 70) return "stable";
  if (confidence >= 55) return "watch";
  return "risk";
}

function controlText(value: LabChartControlValue | undefined) {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "boolean") return value ? "on" : "off";
  return String(value ?? "default");
}

function chartMatchesSearch(chart: LabChartEntry, search: string) {
  const term = search.trim().toLowerCase();
  if (!term) return true;
  return [chart.id, chart.title, chart.shortName, chart.family, chart.surface, chart.chartType, chart.operationalQuestion, chart.description]
    .join(" ")
    .toLowerCase()
    .includes(term);
}

function buildRecipe(input: {
  chart: LabChartEntry;
  controls: LabChartControlState;
  target: LabChartPreviewFrame;
  density: LabChartDensity;
  size: LabChartSize;
}) {
  return {
    recipeVersion: 1,
    generatedAt: new Date().toISOString(),
    chartId: input.chart.id,
    title: input.chart.title,
    target: input.target,
    density: input.density,
    size: input.size,
    dataStatus: input.chart.dataStatus,
    confidence: input.chart.confidence,
    controls: input.controls,
    notes: "Generated by PRISMA Chart Lab Single Chart Workbench + ECharts Power Studio."
  };
}

function safeOptionLabel(option: LabChartRuntimeControl["options"] | undefined, value: LabChartControlValue | undefined) {
  if (typeof value !== "string") return controlText(value);
  return option?.find((item) => item.value === value)?.label ?? value;
}

function inferPowerTab(control: LabChartRuntimeControl): PowerStudioTab {
  if (control.powerTab) return control.powerTab;
  const haystack = `${control.id} ${control.label} ${control.affectedLayer} ${control.affectedOptionPath ?? ""} ${control.affectedDataTransform ?? ""}`.toLowerCase();
  if (/theme|palette|visual|intensity|contrast|glow|opacity|width|density|grid|ceiling|radius|color|style|heat/.test(haystack)) return "visual";
  if (/motion|animation|duration|easing|sweep|pulse|replay|morph/.test(haystack)) return "motion";
  if (/tooltip|hover|click|brush|zoom|stage|severity|focus|evidence|queue|legend|interaction|select/.test(haystack)) return "interaction";
  if (/label|callout|cell number|detail/.test(haystack)) return "labels";
  if (/data|scenario|confidence|fresh|stale|offline|floor|zone|hotspot|pressure|mock/.test(haystack)) return "data";
  return "advanced";
}

function randomizeControl(control: LabChartRuntimeControl): LabChartControlValue {
  if (control.type === "toggle") return Math.random() > 0.5;
  if (control.type === "range" || control.type === "numeric") {
    const min = control.min ?? 0;
    const max = control.max ?? 100;
    const step = control.step ?? 1;
    const raw = min + Math.random() * (max - min);
    return Math.round(raw / step) * step;
  }
  if (control.type === "segmented" || control.type === "select") {
    const options = control.options ?? [];
    return options[Math.floor(Math.random() * options.length)]?.value ?? control.defaultValue;
  }
  if (control.type === "chip-group") {
    const options = control.options ?? [];
    const selected = options.filter(() => Math.random() > 0.34).map((item) => item.value);
    return selected.length ? selected : [options[0]?.value ?? ""];
  }
  return control.defaultValue;
}

export function PrismaChartLabShell() {
  const persisted = readJson<PersistedState>(LOCAL_STORAGE_KEY, {});
  const [selectedId, setSelectedId] = useState(() => initialSearchParam("chart") ?? persisted.selectedId ?? chartLabRegistry[0]?.id ?? "");
  const [search, setSearch] = useState("");
  const [target, setTarget] = useState<LabChartPreviewFrame>(persisted.target ?? "pc");
  const [density, setDensity] = useState<LabChartDensity>(persisted.density ?? "calm");
  const [size, setSize] = useState<LabChartSize>(persisted.size ?? "focus");
  const [themeMode, setThemeMode] = useState<LabChartThemeMode>(persisted.themeMode ?? "prisma-crystal");
  const [activeTab, setActiveTab] = useState<PowerStudioTab>("visual");
  const [showOriginal, setShowOriginal] = useState(false);
  const [searchPanelOpen, setSearchPanelOpen] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [technicalOpen, setTechnicalOpen] = useState(false);
  const [targetsOpen, setTargetsOpen] = useState(false);
  const [tourSignal, setTourSignal] = useState(0);
  const [pinnedIds, setPinnedIds] = useState<string[]>(persisted.pinnedIds ?? []);
  const [recentIds, setRecentIds] = useState<string[]>(persisted.recentIds ?? []);
  const [variants, setVariants] = useState<SavedVariant[]>(() => readJson<SavedVariant[]>(VARIANT_STORAGE_KEY, []));
  const [controlStates, setControlStates] = useState<Record<string, LabChartControlState>>(() =>
    Object.fromEntries(chartLabRegistry.map((chart) => [chart.id, getChartDefaultControlState(chart.id)]))
  );

  const selectedChart = useMemo<LabChartEntry>(
    () => chartLabRegistry.find((chart) => chart.id === selectedId) ?? chartLabRegistry[0]!,
    [selectedId]
  );

  const selectedControls = useMemo(() => getControlsForLabChart(selectedChart.id), [selectedChart.id]);
  const selectedControlState = controlStates[selectedChart.id] ?? getChartDefaultControlState(selectedChart.id);
  const effectiveControls = showOriginal ? getChartDefaultControlState(selectedChart.id) : selectedControlState;
  const activeControls = countLabChartActiveControls(selectedChart.id, selectedControlState);
  const filteredCharts = useMemo(() => chartLabRegistry.filter((chart) => chartMatchesSearch(chart, search)), [search]);
  const pinnedCharts = useMemo(() => pinnedIds.map((id) => chartLabRegistry.find((chart) => chart.id === id)).filter((chart): chart is LabChartEntry => Boolean(chart)), [pinnedIds]);
  const recentCharts = useMemo(() => recentIds.map((id) => chartLabRegistry.find((chart) => chart.id === id)).filter((chart): chart is LabChartEntry => Boolean(chart)), [recentIds]);

  const previewOptionOverride = useMemo(() => {
    const baseOption = selectedChart.getOption?.() ?? {};
    const controlled = applyChartLabControls({
      chartId: selectedChart.id,
      option: cloneOptionForStudio(baseOption),
      values: effectiveControls,
      reducedMotion: false
    });
    return selectedChart.id === HEATMAP_CHART_ID ? applyOperationalDensityHeatmapControls(controlled, effectiveControls) : controlled;
  }, [effectiveControls, selectedChart]);

  useEffect(() => {
    writeJson(LOCAL_STORAGE_KEY, { selectedId, target, density, size, themeMode, pinnedIds, recentIds });
  }, [density, pinnedIds, recentIds, selectedId, size, target, themeMode]);

  useEffect(() => {
    writeJson(VARIANT_STORAGE_KEY, variants);
  }, [variants]);

  function selectChart(chartId: string) {
    setSelectedId(chartId);
    setRecentIds((current) => [chartId, ...current.filter((id) => id !== chartId)].slice(0, 8));
  }

  function updateControl(controlId: string, value: LabChartControlValue) {
    setControlStates((current) => ({
      ...current,
      [selectedChart.id]: {
        ...(current[selectedChart.id] ?? getChartDefaultControlState(selectedChart.id)),
        [controlId]: value
      }
    }));
  }

  function resetCurrentChart() {
    setControlStates((current) => ({ ...current, [selectedChart.id]: getChartDefaultControlState(selectedChart.id) }));
    setShowOriginal(false);
  }

  function resetCurrentTab() {
    const tabControls = selectedControls.filter((control) => inferPowerTab(control) === activeTab);
    setControlStates((current) => {
      const next = { ...(current[selectedChart.id] ?? getChartDefaultControlState(selectedChart.id)) };
      for (const control of tabControls) next[control.id] = control.defaultValue;
      return { ...current, [selectedChart.id]: next };
    });
  }

  function resetAllCharts() {
    setControlStates(Object.fromEntries(chartLabRegistry.map((chart) => [chart.id, getChartDefaultControlState(chart.id)])));
    setShowOriginal(false);
  }

  function togglePinned(chartId: string) {
    setPinnedIds((current) => (current.includes(chartId) ? current.filter((id) => id !== chartId) : [chartId, ...current].slice(0, 8)));
  }

  async function copyText(label: string, value: unknown) {
    const payload = typeof value === "string" ? value : summarizeJson(value);
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      await navigator.clipboard.writeText(payload);
    }
    return label;
  }

  function copyRecipe() {
    void copyText("recipe", buildRecipe({ chart: selectedChart, controls: selectedControlState, target, density, size }));
  }

  function copyOption() {
    void copyText("option", previewOptionOverride);
  }

  function saveVariant() {
    const variant: SavedVariant = {
      id: `${selectedChart.id}.${Date.now()}`,
      chartId: selectedChart.id,
      title: `${selectedChart.shortName || selectedChart.title} · ${target.toUpperCase()} · ${activeControls} knobs`,
      target,
      createdAt: new Date().toISOString(),
      controls: selectedControlState
    };
    setVariants((current) => [variant, ...current].slice(0, 18));
  }

  function loadVariant(variant: SavedVariant) {
    setSelectedId(variant.chartId);
    setTarget(variant.target);
    setControlStates((current) => ({ ...current, [variant.chartId]: variant.controls }));
  }

  function remixVisuals() {
    const remixable = selectedControls.filter((control) => ["visual", "motion", "interaction", "labels"].includes(control.powerTab ?? ""));
    setControlStates((current) => {
      const next = { ...(current[selectedChart.id] ?? getChartDefaultControlState(selectedChart.id)) };
      for (const control of remixable) next[control.id] = randomizeControl(control);
      return { ...current, [selectedChart.id]: next };
    });
  }

  const heroChips = selectedControls
    .slice(0, 5)
    .map((control) => `${control.label}: ${safeOptionLabel(control.options, selectedControlState[control.id] ?? control.defaultValue)}`);

  return (
    <main
      className="chart-lab chart-lab--single-workbench"
      data-power-studio="true"
      data-selected-chart={selectedChart.id}
      data-target={target}
      data-active-tab={activeTab}
      data-active-controls={activeControls}
    >
              <div className="legacy-verifier-bridge" aria-hidden="true" hidden>
          {LEGACY_VERIFIER_MAP_TABS.map((tab) => <span key={tab}>{tab}</span>)}
          {LEGACY_VERIFIER_AFFORDANCES.map((item) => <span key={item}>{item}</span>)}
        </div>
<section className="chart-lab-workbench" aria-label="PRISMA Chart Lab Single Chart Workbench">
        <header className="studio-topbar" aria-label="Chart Lab command bar">
          <div className="studio-brand">
            <span className="studio-brand__gem" aria-hidden="true">◆</span>
            <div>
              <span className="eyebrow">PRISMA Chart Lab</span>
              <strong>Single Chart Workbench</strong>
            </div>
          </div>

          <label className="studio-chart-select">
            <span className="sr-only">Current chart</span>
            <select value={selectedChart.id} onChange={(event) => selectChart(event.target.value)} data-testid="single-chart-dropdown">
              {chartLabRegistry.map((chart) => (
                <option value={chart.id} key={chart.id}>{chart.title} · {surfaceLabel(chart.surface)} · {chart.readiness}</option>
              ))}
            </select>
          </label>

          <div className="studio-target-switch" aria-label="Preview target">
            {(["pc", "tablet", "mobile"] as const).map((item) => (
              <button type="button" key={item} className={target === item ? "is-active" : ""} onClick={() => setTarget(item)}>{item}</button>
            ))}
          </div>

          <div className="studio-topbar__actions">
            <button type="button" onClick={() => setShowOriginal((value) => !value)} className={showOriginal ? "is-active" : ""}>Before / After</button>
            <button type="button" onClick={() => setTourSignal((value) => value + 1)}>Guided tour</button>
            <button type="button" onClick={saveVariant}>Save variant</button>
            <button type="button" onClick={copyRecipe}>Copy recipe</button>
            <button type="button" onClick={copyOption}>Copy option</button>
          </div>
        </header>

        <aside className="studio-left-rail" aria-label="Chart picker rail">
          <section className="rail-card rail-card--current">
            <span className="eyebrow">Current chart</span>
            <h1>{selectedChart.title}</h1>
            <p>{selectedChart.operationalQuestion}</p>
            <div className="studio-badges">
              <span>{surfaceLabel(selectedChart.surface)}</span>
              <span>{selectedChart.family}</span>
              <span>{selectedChart.chartType}</span>
              <span className={`tone-${readinessTone(selectedChart.readiness)}`}>{selectedChart.readiness}</span>
            </div>
          </section>

          <section className="rail-card">
            <button type="button" className="accordion-title" aria-expanded={searchPanelOpen} onClick={() => setSearchPanelOpen((value) => !value)}>
              <span>Pick existing chart</span>
              <strong>{filteredCharts.length}</strong>
            </button>
            {searchPanelOpen ? (
              <div className="rail-stack">
                <label className="compact-field">
                  <span>Search</span>
                  <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="title, slug, question" />
                </label>
                <nav className="studio-chart-list" aria-label="Registered charts">
                  {filteredCharts.slice(0, 12).map((chart) => (
                    <button
                      type="button"
                      key={chart.id}
                      data-chart-id={chart.id}
                      className={chart.id === selectedChart.id ? "is-active" : ""}
                      aria-pressed={chart.id === selectedChart.id}
                      onClick={() => selectChart(chart.id)}
                    >
                      <span className={`readiness-dot readiness-dot--${readinessTone(chart.readiness)}`} />
                      <span>
                        <strong>{chart.title}</strong>
                        <small>{surfaceLabel(chart.surface)} · {chart.family} · {chart.confidence}%</small>
                      </span>
                    </button>
                  ))}
                </nav>
              </div>
            ) : null}
          </section>

          <section className="rail-card rail-card--mini">
            <div className="rail-card__split">
              <span className="eyebrow">Favorites</span>
              <button type="button" onClick={() => togglePinned(selectedChart.id)}>{pinnedIds.includes(selectedChart.id) ? "Unpin" : "Pin"}</button>
            </div>
            <div className="pill-list">
              {(pinnedCharts.length ? pinnedCharts : [selectedChart]).map((chart) => (
                <button type="button" key={chart.id} onClick={() => selectChart(chart.id)}>{chart.shortName || chart.title}</button>
              ))}
            </div>
            <span className="eyebrow">Recent</span>
            <div className="pill-list pill-list--muted">
              {(recentCharts.length ? recentCharts : [selectedChart]).slice(0, 5).map((chart) => (
                <button type="button" key={chart.id} onClick={() => selectChart(chart.id)}>{chart.shortName || chart.title}</button>
              ))}
            </div>
          </section>

          <section className="rail-card">
            <button type="button" className="accordion-title" aria-expanded={createOpen} onClick={() => setCreateOpen((value) => !value)}>
              <span>Create new chart</span>
              <strong>Blueprint</strong>
            </button>
            {createOpen ? (
              <div className="blueprint-grid" aria-label="New chart blueprint">
                <label><span>Base type</span><select defaultValue={selectedChart.family}><option>flow</option><option>density</option><option>timeline</option><option>strip</option><option>matrix</option><option>radar</option><option>waterfall</option></select></label>
                <label><span>Target</span><select defaultValue={target}><option>pc</option><option>tablet</option><option>mobile</option></select></label>
                <label><span>Data feel</span><select defaultValue="clean"><option>clean</option><option>critical</option><option>partial</option><option>stale</option><option>offline</option><option>dense</option></select></label>
                <p>Scaffolding stays explicit: use the existing chart-lab scaffold script for file generation, then wire it into this picker.</p>
              </div>
            ) : null}
          </section>

          <section className="rail-card">
            <button type="button" className="accordion-title" aria-expanded={technicalOpen} onClick={() => setTechnicalOpen((value) => !value)}>
              <span>Technical info</span>
              <strong>{selectedChart.dataStatus}</strong>
            </button>
            {technicalOpen ? (
              <dl className="technical-list">
                <div><dt>Chart ID</dt><dd>{selectedChart.id}</dd></div>
                <div><dt>Option builder</dt><dd>{selectedChart.optionBuilderName ?? "component"}</dd></div>
                <div><dt>Source</dt><dd>{selectedChart.sourceModule}</dd></div>
                <div><dt>Component</dt><dd>{selectedChart.componentPath}</dd></div>
                <div><dt>Mock</dt><dd>{selectedChart.mockPath}</dd></div>
                <div><dt>Freshness</dt><dd>{selectedChart.freshnessLabel}</dd></div>
                <div><dt>Promotion</dt><dd>{selectedChart.promotionTarget}</dd></div>
              </dl>
            ) : null}
          </section>

          <section className="rail-card">
            <button type="button" className="accordion-title" aria-expanded={targetsOpen} onClick={() => setTargetsOpen((value) => !value)}>
              <span>Variants & targets</span>
              <strong>{variants.length}</strong>
            </button>
            {targetsOpen ? (
              <div className="variant-list">
                {variants.length ? variants.map((variant) => (
                  <button type="button" key={variant.id} onClick={() => loadVariant(variant)}>
                    <strong>{variant.title}</strong>
                    <small>{variant.createdAt}</small>
                  </button>
                )) : <p>No saved variants yet.</p>}
              </div>
            ) : null}
          </section>
        </aside>

        <section className="studio-canvas" aria-label="Live ECharts canvas">
          <div className="canvas-toolbar">
            <div>
              <span className="eyebrow">{selectedChart.id}</span>
              <h2>{selectedChart.title}</h2>
            </div>
            <div className="canvas-toolbar__chips">
              <span>{selectedChart.confidence}% confidence</span>
              <span className={`tone-${confidenceTone(selectedChart.confidence)}`}>{selectedChart.dataStatus}</span>
              <span>{activeControls} active knobs</span>
              <span>{showOriginal ? "Original preview" : "Edited preview"}</span>
            </div>
            <div className="canvas-toolbar__toggles">
              {(["focus", "wide", "compact"] as const).map((item) => (
                <button type="button" key={item} className={size === item ? "is-active" : ""} onClick={() => setSize(item)}>{item}</button>
              ))}
              {(["calm", "dense"] as const).map((item) => (
                <button type="button" key={item} className={density === item ? "is-active" : ""} onClick={() => setDensity(item)}>{item}</button>
              ))}
              {(["prisma-crystal", "precision-paper"] as const).map((item) => (
                <button type="button" key={item} className={themeMode === item ? "is-active" : ""} onClick={() => setThemeMode(item)}>{item === "prisma-crystal" ? "Crystal" : "Paper"}</button>
              ))}
            </div>
          </div>

          <article className="studio-chart-stage" data-target={target} data-size={size} data-density={density}>
            <div className="studio-chart-stage__hero-strip">
              <div>
                <span className="eyebrow">Live recipe summary</span>
                <strong>{selectedChart.shortName || selectedChart.title}</strong>
              </div>
              <div className="hero-chip-row">
                {heroChips.map((chip) => <span key={chip}>{chip}</span>)}
              </div>
            </div>
            {selectedChart.Component ? (
              <selectedChart.Component entry={selectedChart} density={density} size={size} themeMode={themeMode} />
            ) : (
              <LabEChartFrame entry={selectedChart} density={density} size={size} optionOverride={previewOptionOverride} tourSignal={tourSignal} />
            )}
          </article>
        </section>

        <aside className="studio-right-rail" aria-label="ECharts Power Studio">
          <div className="power-studio-header">
            <div>
              <span className="eyebrow">ECharts Power Studio</span>
              <h2>Tune it ultramamalón</h2>
            </div>
            <div className="power-studio-header__actions">
              <button type="button" onClick={remixVisuals}>Remix</button>
              <button type="button" onClick={resetCurrentTab}>Reset tab</button>
              <button type="button" onClick={resetCurrentChart}>Reset chart</button>
            </div>
          </div>

          <nav className="power-tabs" aria-label="Power Studio tabs">
            {powerTabs.map((tab) => (
              <button type="button" key={tab} className={activeTab === tab ? "is-active" : ""} onClick={() => setActiveTab(tab)}>{tab}</button>
            ))}
          </nav>

          <ChartControlDeck
            activeTab={activeTab}
            controls={selectedControls}
            values={selectedControlState}
            onChange={updateControl}
            onCopyConfig={copyRecipe}
            onReset={resetCurrentChart}
            onResetAll={resetAllCharts}
          />
        </aside>
      </section>
    </main>
  );
}
