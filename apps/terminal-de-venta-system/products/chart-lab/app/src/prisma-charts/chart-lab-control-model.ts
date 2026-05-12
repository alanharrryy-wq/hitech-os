import type {
  LabChartControlState,
  LabChartControlValue,
  LabChartRuntimeControl,
  LabChartScenario,
  LabChartThemePreset
} from "./chart-lab-types";

const severityOptions = ["INFO", "WARN", "ERROR", "CRITICAL"].map((value) => ({ label: value, value }));
const scenarioOptions = [
  { label: "Clean", value: "clean" },
  { label: "Critical", value: "critical" },
  { label: "Partial", value: "partial" },
  { label: "Stale", value: "stale" },
  { label: "Offline", value: "offline" },
  { label: "Dense", value: "dense" }
];
const themeOptions = [
  { label: "Crystal Light", value: "crystal-light" },
  { label: "Executive Dense", value: "executive-dense" },
  { label: "Forensic", value: "forensic" },
  { label: "High Contrast", value: "high-contrast" }
];

function control(input: LabChartRuntimeControl): LabChartRuntimeControl {
  return input;
}

function commonChartControls(extra: LabChartRuntimeControl[] = []): LabChartRuntimeControl[] {
  return [
    control({
      id: "dataScenario",
      label: "Data scenario",
      type: "select",
      defaultValue: "clean",
      options: scenarioOptions,
      affectedLayer: "data",
      affectedDataTransform: "scales or suppresses mock values to preview state behavior",
      validation: "value must be one of clean, critical, partial, stale, offline, dense",
      risk: "low",
      resetBehavior: "returns to clean"
    }),
    control({
      id: "themePreset",
      label: "Theme preset",
      type: "segmented",
      defaultValue: "crystal-light",
      options: themeOptions,
      affectedLayer: "visual recipe",
      affectedOptionPath: "option.color / option.backgroundColor / textStyle",
      validation: "value must be a known lab theme preset",
      risk: "low",
      resetBehavior: "returns to Crystal Light"
    }),
    control({
      id: "showLabels",
      label: "Labels",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "chart marks",
      affectedOptionPath: "series[].label.show",
      validation: "boolean",
      risk: "low",
      resetBehavior: "labels on"
    }),
    control({
      id: "animation",
      label: "Animation",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "motion",
      affectedOptionPath: "option.animation",
      validation: "boolean; disabled when reduced motion is active",
      risk: "low",
      resetBehavior: "animation on"
    }),
    control({
      id: "visualIntensity",
      label: "Visual intensity",
      type: "range",
      defaultValue: 70,
      min: 20,
      max: 100,
      step: 5,
      affectedLayer: "marks",
      affectedOptionPath: "series[].itemStyle.opacity / lineStyle.width",
      validation: "20-100",
      risk: "medium",
      resetBehavior: "returns to 70"
    }),
    ...extra
  ];
}

export const chartControlSchemas: Record<string, LabChartRuntimeControl[]> = {
  "pc.causal-flow-ribbon": commonChartControls([
    control({
      id: "severityFilter",
      label: "Severity",
      type: "chip-group",
      defaultValue: ["INFO", "WARN", "ERROR", "CRITICAL"],
      options: severityOptions,
      affectedLayer: "data links",
      affectedDataTransform: "filters sankey links by datum.severity",
      validation: "one or more known severity values",
      risk: "medium",
      resetBehavior: "all severities enabled"
    }),
    control({
      id: "confidenceFloor",
      label: "Confidence floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "data links",
      affectedDataTransform: "filters links below confidence threshold",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "ribbonWidth",
      label: "Ribbon width",
      type: "range",
      defaultValue: 14,
      min: 8,
      max: 26,
      step: 1,
      affectedLayer: "geometry",
      affectedOptionPath: "series[0].nodeWidth",
      validation: "8-26",
      risk: "medium",
      resetBehavior: "14"
    }),
    control({
      id: "ribbonOpacity",
      label: "Ribbon opacity",
      type: "range",
      defaultValue: 46,
      min: 18,
      max: 80,
      step: 2,
      affectedLayer: "links",
      affectedOptionPath: "series[0].links[].lineStyle.opacity",
      validation: "18-80",
      risk: "medium",
      resetBehavior: "46"
    }),
    control({
      id: "detailLevel",
      label: "Detail level",
      type: "segmented",
      defaultValue: "standard",
      options: [
        { label: "Calm", value: "calm" },
        { label: "Standard", value: "standard" },
        { label: "Forensic", value: "forensic" }
      ],
      affectedLayer: "labels/tooltips",
      affectedOptionPath: "series[0].label / tooltip",
      validation: "calm, standard, forensic",
      risk: "low",
      resetBehavior: "standard"
    }),
    control({
      id: "stageFocus",
      label: "Stage focus",
      type: "select",
      defaultValue: "all",
      options: [
        { label: "All stages", value: "all" },
        { label: "Source", value: "sourceModule" },
        { label: "Cause", value: "causeType" },
        { label: "Effect", value: "effectType" },
        { label: "Action", value: "actionTarget" }
      ],
      affectedLayer: "data links",
      affectedDataTransform: "keeps links connected to the selected causal stage",
      validation: "known causal stage",
      risk: "medium",
      resetBehavior: "all"
    }),
    control({
      id: "layoutDensity",
      label: "Layout density",
      type: "segmented",
      defaultValue: "balanced",
      options: [
        { label: "Airy", value: "airy" },
        { label: "Balanced", value: "balanced" },
        { label: "Dense", value: "dense" }
      ],
      affectedLayer: "layout",
      affectedOptionPath: "series[0].nodeGap / layoutIterations",
      validation: "airy, balanced, dense",
      risk: "medium",
      resetBehavior: "balanced"
    }),
    control({
      id: "evidenceMode",
      label: "Evidence mode",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "tooltip/labels",
      affectedOptionPath: "series[0].edgeLabel.show",
      validation: "boolean",
      risk: "low",
      resetBehavior: "enabled"
    })
  ]),
  "pc.operational-density-field": commonChartControls([
    control({
      id: "pressureFloor",
      label: "Pressure floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "heatmap data",
      affectedDataTransform: "filters heatmap cells below pressure",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "moduleSearch",
      label: "Module search",
      type: "search",
      defaultValue: "",
      affectedLayer: "heatmap rows",
      affectedDataTransform: "filters y-axis modules",
      validation: "plain text",
      risk: "low",
      resetBehavior: "empty"
    })
  ]),
  "pc.service-dependency-graph": commonChartControls([
    control({
      id: "dependencyStatus",
      label: "Dependency status",
      type: "chip-group",
      defaultValue: ["PASS", "DEGRADED", "FAIL", "UNKNOWN"],
      options: ["PASS", "DEGRADED", "FAIL", "UNKNOWN"].map((value) => ({ label: value, value })),
      affectedLayer: "graph nodes",
      affectedDataTransform: "filters nodes and edges by status",
      validation: "one or more known status values",
      risk: "medium",
      resetBehavior: "all statuses enabled"
    }),
    control({
      id: "forceRepulsion",
      label: "Repulsion",
      type: "range",
      defaultValue: 210,
      min: 90,
      max: 420,
      step: 10,
      affectedLayer: "layout physics",
      affectedOptionPath: "series[0].force.repulsion",
      validation: "90-420",
      risk: "medium",
      resetBehavior: "210"
    })
  ]),
  "pc.inventory-risk-treemap": commonChartControls([
    control({
      id: "riskFloor",
      label: "Risk floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "treemap nodes",
      affectedDataTransform: "filters low-risk nodes",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "leafDepth",
      label: "Leaf depth",
      type: "segmented",
      defaultValue: "category",
      options: [
        { label: "Category", value: "category" },
        { label: "SKU", value: "sku" }
      ],
      affectedLayer: "treemap hierarchy",
      affectedOptionPath: "series[0].leafDepth",
      validation: "category or sku",
      risk: "low",
      resetBehavior: "category"
    })
  ]),
  "pc.decision-ledger-timeline": commonChartControls([
    control({
      id: "impactFloor",
      label: "Impact floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "timeline points",
      affectedDataTransform: "filters decision points below impact",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "pc.financial-operational-waterfall": commonChartControls([
    control({
      id: "moneyScale",
      label: "Money scale",
      type: "range",
      defaultValue: 100,
      min: 50,
      max: 150,
      step: 5,
      affectedLayer: "waterfall values",
      affectedDataTransform: "scales operational money impact for stress testing",
      validation: "50-150",
      risk: "medium",
      resetBehavior: "100"
    })
  ]),
  "tablet.shift-pulse-strip": commonChartControls([
    control({
      id: "queueFloor",
      label: "Queue floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 80,
      step: 5,
      affectedLayer: "shift buckets",
      affectedDataTransform: "filters low-pressure buckets",
      validation: "0-80",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "tablet.sync-outbox-status-matrix": commonChartControls([
    control({
      id: "syncState",
      label: "Sync state",
      type: "select",
      defaultValue: "all",
      options: [
        { label: "All", value: "all" },
        { label: "Pending", value: "pending" },
        { label: "Failed", value: "failed" },
        { label: "Retrying", value: "retrying" },
        { label: "Sent", value: "sent" }
      ],
      affectedLayer: "matrix columns",
      affectedDataTransform: "filters matrix cells by sync state",
      validation: "known sync state or all",
      risk: "medium",
      resetBehavior: "all"
    }),
    control({
      id: "blockingOnly",
      label: "Blocking only",
      type: "toggle",
      defaultValue: false,
      affectedLayer: "matrix cells",
      affectedDataTransform: "keeps only blocking cells",
      validation: "boolean",
      risk: "medium",
      resetBehavior: "off"
    })
  ]),
  "mobile.owner-pulse-timeline": commonChartControls([
    control({
      id: "healthFloor",
      label: "Health floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "timeline",
      affectedDataTransform: "filters points below health floor",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "mobile.action-inbox-priority-stack": commonChartControls([
    control({
      id: "ownerSearch",
      label: "Owner search",
      type: "search",
      defaultValue: "",
      affectedLayer: "owner stack",
      affectedDataTransform: "filters owner rows by text",
      validation: "plain text",
      risk: "low",
      resetBehavior: "empty"
    })
  ]),
  "mobile.health-radar-compact": commonChartControls([
    control({
      id: "radarFill",
      label: "Radar fill",
      type: "range",
      defaultValue: 18,
      min: 0,
      max: 45,
      step: 1,
      affectedLayer: "radar area",
      affectedOptionPath: "series[0].data[0].areaStyle.opacity",
      validation: "0-45",
      risk: "medium",
      resetBehavior: "18"
    })
  ]),
  "mobile.freshness-beacon-grid": commonChartControls([
    control({
      id: "freshnessFloor",
      label: "Freshness floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "freshness beacons",
      affectedDataTransform: "filters low freshness scores",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "mobile.incident-spark-cards": commonChartControls([
    control({
      id: "sparkSmoothing",
      label: "Spark smoothing",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "line shape",
      affectedOptionPath: "series[0].smooth",
      validation: "boolean",
      risk: "low",
      resetBehavior: "on"
    })
  ]),
  "mobile.confidence-meter-bands": commonChartControls([
    control({
      id: "bandFloor",
      label: "Band floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "confidence bands",
      affectedDataTransform: "filters bands below confidence",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "example.future-chart": [
    control({
      id: "disabledPlaceholder",
      label: "Placeholder controls",
      type: "toggle",
      defaultValue: false,
      affectedLayer: "none",
      validation: "disabled until chart 15 is promoted into a real option builder",
      risk: "low",
      resetBehavior: "off",
      disabledReason: "Example chart is visual scaffolding only."
    })
  ]
};

export function getControlsForChart(chartId: string): LabChartRuntimeControl[] {
  return chartControlSchemas[chartId] ?? [];
}

export function getDefaultControlState(chartId: string): LabChartControlState {
  return Object.fromEntries(getControlsForChart(chartId).map((item) => [item.id, item.defaultValue]));
}

export function countActiveControls(chartId: string, values: LabChartControlState): number {
  return getControlsForChart(chartId).filter((controlDef) => {
    const current = values[controlDef.id] ?? controlDef.defaultValue;
    return JSON.stringify(current) !== JSON.stringify(controlDef.defaultValue);
  }).length;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function seriesArray(option: Record<string, unknown>): Record<string, unknown>[] {
  const series = option.series;
  if (Array.isArray(series)) return series.filter(isRecord);
  if (isRecord(series)) return [series];
  return [];
}

function numeric(value: LabChartControlValue | undefined, fallback: number): number {
  return typeof value === "number" ? value : fallback;
}

function stringValue(value: LabChartControlValue | undefined, fallback: string): string {
  return typeof value === "string" ? value : fallback;
}

function booleanValue(value: LabChartControlValue | undefined, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function stringList(value: LabChartControlValue | undefined, fallback: string[]): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : fallback;
}

function scenarioMultiplier(scenario: LabChartScenario): number {
  if (scenario === "critical") return 1.24;
  if (scenario === "partial") return 0.68;
  if (scenario === "stale") return 0.82;
  if (scenario === "offline") return 0;
  if (scenario === "dense") return 1.1;
  return 1;
}

function scaleDatum(value: unknown, multiplier: number): unknown {
  if (typeof value === "number") return Math.max(0, Math.round(value * multiplier));
  if (Array.isArray(value)) {
    const next = [...value];
    let scaleIndex = -1;
    for (let index = next.length - 1; index > 1; index -= 1) {
      if (typeof next[index] === "number") {
        scaleIndex = index;
        break;
      }
    }
    if (scaleIndex >= 0) next[scaleIndex] = scaleDatum(next[scaleIndex], multiplier);
    return next;
  }
  if (isRecord(value)) {
    if (typeof value.value === "number") value.value = scaleDatum(value.value, multiplier);
    if (Array.isArray(value.value)) value.value = scaleDatum(value.value, multiplier);
    if (typeof value.symbolSize === "number") value.symbolSize = Math.max(4, Math.round(value.symbolSize * Math.min(1.25, multiplier || 0.4)));
    return value;
  }
  return value;
}

function applyScenario(option: Record<string, unknown>, scenario: LabChartScenario): void {
  const multiplier = scenarioMultiplier(scenario);
  for (const series of seriesArray(option)) {
    if (Array.isArray(series.data)) {
      series.data = scenario === "empty" ? [] : series.data.map((item) => scaleDatum(item, multiplier));
    }
    if (Array.isArray(series.links)) {
      series.links = scenario === "empty" ? [] : series.links.map((item) => scaleDatum(item, multiplier));
    }
  }
  const title = option.title;
  if (isRecord(title)) {
    title.subtext = `${String(title.subtext ?? "")} | scenario=${scenario} mock/demo`;
  }
}

function applyThemePreset(option: Record<string, unknown>, themePreset: LabChartThemePreset): void {
  const palette: Record<LabChartThemePreset, string[]> = {
    "crystal-light": ["#086dff", "#63dfff", "#13b981", "#e59b2a", "#df3d2f", "#7557ff"],
    "executive-dense": ["#0f172a", "#2563eb", "#0d9488", "#ca8a04", "#be123c", "#6d28d9"],
    forensic: ["#111827", "#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"],
    "high-contrast": ["#000000", "#005fcc", "#008a00", "#c05a00", "#d10000", "#5900cc"]
  };
  option.color = palette[themePreset];
  if (themePreset === "high-contrast") option.backgroundColor = "#ffffff";
}

function applySeriesLabels(option: Record<string, unknown>, show: boolean): void {
  for (const series of seriesArray(option)) {
    const label = isRecord(series.label) ? series.label : {};
    label.show = show;
    series.label = label;
  }
}

function applyVisualIntensity(option: Record<string, unknown>, intensity: number): void {
  const opacity = Math.max(0.2, Math.min(1, intensity / 100));
  const widthBoost = Math.max(1, Math.round(intensity / 28));
  for (const series of seriesArray(option)) {
    const itemStyle = isRecord(series.itemStyle) ? series.itemStyle : {};
    itemStyle.opacity = opacity;
    series.itemStyle = itemStyle;
    const lineStyle = isRecord(series.lineStyle) ? series.lineStyle : {};
    if (Object.keys(lineStyle).length > 0) lineStyle.width = widthBoost;
    series.lineStyle = lineStyle;
  }
}

function datumConfidence(item: unknown): number | null {
  if (isRecord(item) && typeof item.confidence === "number") return item.confidence;
  if (isRecord(item) && isRecord(item.item) && typeof item.item.confidence === "number") return item.item.confidence;
  if (Array.isArray(item)) {
    for (const part of item) {
      if (isRecord(part) && typeof part.confidence === "number") return part.confidence;
    }
  }
  return null;
}

function filterByConfidence(option: Record<string, unknown>, floor: number): void {
  if (floor <= 0) return;
  for (const series of seriesArray(option)) {
    if (Array.isArray(series.data)) series.data = series.data.filter((item) => (datumConfidence(item) ?? 100) >= floor);
    if (Array.isArray(series.links)) series.links = series.links.filter((item) => (datumConfidence(item) ?? 100) >= floor);
  }
}

function applyCausalControls(option: Record<string, unknown>, values: LabChartControlState): void {
  const series = seriesArray(option)[0];
  if (!series) return;
  const severities = stringList(values.severityFilter, ["INFO", "WARN", "ERROR", "CRITICAL"]);
  const confidenceFloor = numeric(values.confidenceFloor, 0);
  const stageFocus = stringValue(values.stageFocus, "all");
  const opacity = numeric(values.ribbonOpacity, 46) / 100;
  const layoutDensity = stringValue(values.layoutDensity, "balanced");
  const detailLevel = stringValue(values.detailLevel, "standard");
  const evidenceMode = booleanValue(values.evidenceMode, true);

  if (Array.isArray(series.links)) {
    series.links = series.links
      .filter((link) => isRecord(link) && isRecord(link.item))
      .filter((link) => severities.includes(String((link as Record<string, Record<string, unknown>>).item.severity ?? "")))
      .filter((link) => Number((link as Record<string, Record<string, unknown>>).item.confidence ?? 100) >= confidenceFloor)
      .filter((link) => {
        if (stageFocus === "all") return true;
        const item = (link as Record<string, Record<string, unknown>>).item;
        return Boolean(item[stageFocus]);
      })
      .map((link) => {
        const record = link as Record<string, unknown>;
        const lineStyle = isRecord(record.lineStyle) ? record.lineStyle : {};
        lineStyle.opacity = opacity;
        record.lineStyle = lineStyle;
        return record;
      });

    const usedNames = new Set<string>();
    for (const link of series.links) {
      if (isRecord(link)) {
        if (typeof link.source === "string") usedNames.add(link.source);
        if (typeof link.target === "string") usedNames.add(link.target);
      }
    }
    if (Array.isArray(series.data)) {
      series.data = series.data.filter((node) => isRecord(node) && typeof node.name === "string" && usedNames.has(node.name));
    }
  }

  series.nodeWidth = numeric(values.ribbonWidth, 14);
  series.nodeGap = layoutDensity === "airy" ? 20 : layoutDensity === "dense" ? 7 : 12;
  series.layoutIterations = layoutDensity === "dense" ? 18 : layoutDensity === "airy" ? 44 : 32;
  const edgeLabel = isRecord(series.edgeLabel) ? series.edgeLabel : {};
  edgeLabel.show = evidenceMode && detailLevel === "forensic";
  series.edgeLabel = edgeLabel;
}

function filterNumericSeriesData(option: Record<string, unknown>, floor: number): void {
  if (floor <= 0) return;
  for (const series of seriesArray(option)) {
    if (!Array.isArray(series.data)) continue;
    series.data = series.data.filter((item) => {
      if (typeof item === "number") return item >= floor;
      if (Array.isArray(item)) return item.some((part) => typeof part === "number" && part >= floor);
      if (isRecord(item) && typeof item.value === "number") return item.value >= floor;
      return true;
    });
  }
}

function applyChartSpecificControls(chartId: string, option: Record<string, unknown>, values: LabChartControlState): void {
  switch (chartId) {
    case "pc.causal-flow-ribbon":
      applyCausalControls(option, values);
      break;
    case "pc.operational-density-field":
      filterNumericSeriesData(option, numeric(values.pressureFloor, 0));
      break;
    case "pc.service-dependency-graph": {
      const series = seriesArray(option)[0];
      if (series && isRecord(series.force)) series.force.repulsion = numeric(values.forceRepulsion, 210);
      break;
    }
    case "pc.inventory-risk-treemap": {
      const series = seriesArray(option)[0];
      if (series) series.leafDepth = stringValue(values.leafDepth, "category") === "sku" ? 2 : 1;
      break;
    }
    case "pc.decision-ledger-timeline":
      filterNumericSeriesData(option, numeric(values.impactFloor, 0));
      break;
    case "pc.financial-operational-waterfall":
      applyScenario(option, numeric(values.moneyScale, 100) > 100 ? "critical" : "clean");
      break;
    case "tablet.shift-pulse-strip":
      filterNumericSeriesData(option, numeric(values.queueFloor, 0));
      break;
    case "mobile.owner-pulse-timeline":
      filterNumericSeriesData(option, numeric(values.healthFloor, 0));
      break;
    case "mobile.health-radar-compact": {
      const firstSeries = seriesArray(option)[0];
      const data = Array.isArray(firstSeries?.data) ? firstSeries.data[0] : null;
      if (isRecord(data)) {
        const areaStyle = isRecord(data.areaStyle) ? data.areaStyle : {};
        areaStyle.opacity = numeric(values.radarFill, 18) / 100;
        data.areaStyle = areaStyle;
      }
      break;
    }
    case "mobile.freshness-beacon-grid":
      filterNumericSeriesData(option, numeric(values.freshnessFloor, 0));
      break;
    case "mobile.incident-spark-cards": {
      const firstSeries = seriesArray(option)[0];
      if (firstSeries) firstSeries.smooth = booleanValue(values.sparkSmoothing, true);
      break;
    }
    case "mobile.confidence-meter-bands":
      filterNumericSeriesData(option, numeric(values.bandFloor, 0));
      break;
    default:
      break;
  }
}

export function applyChartLabControls(input: {
  chartId: string;
  option: Record<string, unknown>;
  values: LabChartControlState;
  reducedMotion: boolean;
}): Record<string, unknown> {
  const scenario = stringValue(input.values.dataScenario, "clean") as LabChartScenario;
  const themePreset = stringValue(input.values.themePreset, "crystal-light") as LabChartThemePreset;
  applyScenario(input.option, scenario);
  applyThemePreset(input.option, themePreset);
  applySeriesLabels(input.option, booleanValue(input.values.showLabels, true));
  applyVisualIntensity(input.option, numeric(input.values.visualIntensity, 70));
  filterByConfidence(input.option, numeric(input.values.confidenceFloor, 0));
  input.option.animation = booleanValue(input.values.animation, true) && !input.reducedMotion;
  applyChartSpecificControls(input.chartId, input.option, input.values);
  return input.option;
}
