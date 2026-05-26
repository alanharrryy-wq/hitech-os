// PRISMA_CHART_LAB_CODE_DRAWERS_V1

export const CODE_DRAWER_IDS = [
  "baseOptionPatch",
  "seriesPatch",
  "itemStylePatch",
  "lineStylePatch",
  "areaStylePatch",
  "labelPatch",
  "visualMapPatch",
  "graphicOverlayPatch",
  "datasetPatch",
  "animationPatch",
  "tooltipFormatter",
  "labelFormatter",
  "rawOptionPatch"
] as const;

export type CodeDrawerId = (typeof CODE_DRAWER_IDS)[number];
export type CodeDrawerKind = "json" | "formatter";
export type CodeDrawerValidationStatus = "Valid" | "Invalid JSON" | "Disabled";

export type CodeDrawerState = {
  id: CodeDrawerId;
  kind: CodeDrawerKind;
  label: string;
  description: string;
  enabled: boolean;
  content: string;
  lastAppliedContent?: string;
};

export type ChartCodeDrawerRecipe = Record<CodeDrawerId, CodeDrawerState>;

export type CodeDrawerValidationResult = {
  id: CodeDrawerId;
  valid: boolean;
  status: CodeDrawerValidationStatus;
  error?: string;
  patch?: unknown;
};

export type CodeDrawerApplyContext = {
  chartId: string;
};

export type CodeDrawerApplyResult = {
  option: Record<string, unknown>;
  appliedDrawerIds: CodeDrawerId[];
  errors: Partial<Record<CodeDrawerId, string>>;
};

const DRAWER_META: Record<CodeDrawerId, Omit<CodeDrawerState, "enabled" | "content" | "lastAppliedContent">> = {
  baseOptionPatch: {
    id: "baseOptionPatch",
    kind: "json",
    label: "Base option patch",
    description: "Deep-merge a JSON object into the root ECharts option after Visual Layers."
  },
  seriesPatch: {
    id: "seriesPatch",
    kind: "json",
    label: "Series patch",
    description: "Patch every series, or provide a root series key to replace/merge the series option."
  },
  itemStylePatch: {
    id: "itemStylePatch",
    kind: "json",
    label: "Item style patch",
    description: "Patch series.itemStyle for direct mark and cell styling."
  },
  lineStylePatch: {
    id: "lineStylePatch",
    kind: "json",
    label: "Line style patch",
    description: "Patch series.lineStyle for lines, graph edges, and sankey links."
  },
  areaStylePatch: {
    id: "areaStylePatch",
    kind: "json",
    label: "Area style patch",
    description: "Patch series.areaStyle without lowering the final visibility guard."
  },
  labelPatch: {
    id: "labelPatch",
    kind: "json",
    label: "Label patch",
    description: "Patch series.label for direct label control."
  },
  visualMapPatch: {
    id: "visualMapPatch",
    kind: "json",
    label: "VisualMap patch",
    description: "Patch option.visualMap while keeping the base chart intact."
  },
  graphicOverlayPatch: {
    id: "graphicOverlayPatch",
    kind: "json",
    label: "Graphic overlays patch",
    description: "Patch option.graphic for annotations and overlays."
  },
  datasetPatch: {
    id: "datasetPatch",
    kind: "json",
    label: "Dataset patch",
    description: "Patch option.dataset for advanced ECharts data wiring."
  },
  animationPatch: {
    id: "animationPatch",
    kind: "json",
    label: "Animation patch",
    description: "Patch root animation keys and transition behavior."
  },
  tooltipFormatter: {
    id: "tooltipFormatter",
    kind: "formatter",
    label: "Tooltip formatter",
    description: "String formatter applied to option.tooltip.formatter only when explicitly enabled."
  },
  labelFormatter: {
    id: "labelFormatter",
    kind: "formatter",
    label: "Label formatter",
    description: "String formatter applied to series.label.formatter only when explicitly enabled."
  },
  rawOptionPatch: {
    id: "rawOptionPatch",
    kind: "json",
    label: "Raw option patch",
    description: "Advanced raw patch applied last before applyChartLabVisibilityGuard."
  }
};

const JSON_DEFAULT = "{\n  \n}";
const FORMATTER_DEFAULT = "";

const DRAWER_APPLICATION_ORDER: CodeDrawerId[] = [
  "baseOptionPatch",
  "seriesPatch",
  "itemStylePatch",
  "lineStylePatch",
  "areaStylePatch",
  "labelPatch",
  "visualMapPatch",
  "graphicOverlayPatch",
  "datasetPatch",
  "animationPatch",
  "tooltipFormatter",
  "labelFormatter",
  "rawOptionPatch"
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function cloneValue<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => cloneValue(item)) as T;
  if (isRecord(value)) {
    const next: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value)) next[key] = cloneValue(item);
    return next as T;
  }
  return value;
}

function assignMergedField(option: Record<string, unknown>, field: string, patch: unknown): Record<string, unknown> {
  const cloned = cloneValue(option);
  if (isRecord(patch) && isRecord(cloned[field])) {
    cloned[field] = safeDeepMergeOption(cloned[field] as Record<string, unknown>, patch);
    return cloned;
  }
  cloned[field] = cloneValue(patch);
  return cloned;
}

function patchSeries(option: Record<string, unknown>, patch: unknown): Record<string, unknown> {
  const cloned = cloneValue(option);
  if (isRecord(patch) && "series" in patch) return safeDeepMergeOption(cloned, patch);
  if (Array.isArray(patch)) {
    cloned.series = cloneValue(patch);
    return cloned;
  }
  if (!isRecord(patch)) return cloned;
  const series = Array.isArray(cloned.series) ? cloned.series : isRecord(cloned.series) ? [cloned.series] : [];
  cloned.series = series.map((item) => (isRecord(item) ? safeDeepMergeOption(item, patch) : item));
  return cloned;
}

function patchSeriesStyle(option: Record<string, unknown>, styleKey: "itemStyle" | "lineStyle" | "areaStyle" | "label", patch: unknown): Record<string, unknown> {
  const cloned = cloneValue(option);
  if (!isRecord(patch)) return cloned;
  const series = Array.isArray(cloned.series) ? cloned.series : isRecord(cloned.series) ? [cloned.series] : [];
  cloned.series = series.map((item) => {
    if (!isRecord(item)) return item;
    const current = isRecord(item[styleKey]) ? (item[styleKey] as Record<string, unknown>) : {};
    return { ...item, [styleKey]: safeDeepMergeOption(current, patch) };
  });
  return cloned;
}

function patchFieldOrRoot(option: Record<string, unknown>, rootKey: "visualMap" | "graphic" | "dataset", patch: unknown): Record<string, unknown> {
  if (isRecord(patch) && rootKey in patch) return safeDeepMergeOption(option, patch);
  return assignMergedField(option, rootKey, patch);
}

function patchTooltipFormatter(option: Record<string, unknown>, formatter: string): Record<string, unknown> {
  const cloned = cloneValue(option);
  const tooltip = isRecord(cloned.tooltip) ? cloned.tooltip : {};
  cloned.tooltip = { ...tooltip, formatter };
  return cloned;
}

function patchLabelFormatter(option: Record<string, unknown>, formatter: string): Record<string, unknown> {
  const cloned = cloneValue(option);
  const series = Array.isArray(cloned.series) ? cloned.series : isRecord(cloned.series) ? [cloned.series] : [];
  cloned.series = series.map((item) => {
    if (!isRecord(item)) return item;
    const label = isRecord(item.label) ? item.label : {};
    return { ...item, label: { ...label, formatter } };
  });
  return cloned;
}

function applyDrawerPatch(option: Record<string, unknown>, drawer: CodeDrawerState, patch: unknown): Record<string, unknown> {
  if (drawer.id === "baseOptionPatch") return isRecord(patch) ? safeDeepMergeOption(option, patch) : option;
  if (drawer.id === "seriesPatch") return patchSeries(option, patch);
  if (drawer.id === "itemStylePatch") return patchSeriesStyle(option, "itemStyle", patch);
  if (drawer.id === "lineStylePatch") return patchSeriesStyle(option, "lineStyle", patch);
  if (drawer.id === "areaStylePatch") return patchSeriesStyle(option, "areaStyle", patch);
  if (drawer.id === "labelPatch") return patchSeriesStyle(option, "label", patch);
  if (drawer.id === "visualMapPatch") return patchFieldOrRoot(option, "visualMap", patch);
  if (drawer.id === "graphicOverlayPatch") return patchFieldOrRoot(option, "graphic", patch);
  if (drawer.id === "datasetPatch") return patchFieldOrRoot(option, "dataset", patch);
  if (drawer.id === "animationPatch") return isRecord(patch) ? safeDeepMergeOption(option, patch) : option;
  if (drawer.id === "tooltipFormatter" && typeof patch === "string") return patchTooltipFormatter(option, patch);
  if (drawer.id === "labelFormatter" && typeof patch === "string") return patchLabelFormatter(option, patch);
  if (drawer.id === "rawOptionPatch") return isRecord(patch) ? safeDeepMergeOption(option, patch) : option;
  return option;
}

export function getDefaultCodeDrawers(chartId: string): ChartCodeDrawerRecipe {
  const defaults = Object.fromEntries(
    CODE_DRAWER_IDS.map((id) => {
      const meta = DRAWER_META[id];
      return [
        id,
        {
          ...meta,
          enabled: false,
          content: meta.kind === "formatter" ? FORMATTER_DEFAULT : JSON_DEFAULT,
          lastAppliedContent: undefined
        }
      ];
    })
  ) as ChartCodeDrawerRecipe;

  defaults.baseOptionPatch.content = `{\n  \"aria\": {\n    \"enabled\": true,\n    \"label\": \"${chartId}\"\n  }\n}`;
  return defaults;
}

export function validateCodeDrawer(drawer: CodeDrawerState): CodeDrawerValidationResult {
  if (!drawer.enabled) return { id: drawer.id, valid: true, status: "Disabled" };
  if (drawer.kind === "formatter") {
    const formatter = drawer.content.trim();
    if (!formatter) {
      return { id: drawer.id, valid: false, status: "Invalid JSON", error: "Formatter drawer is enabled but empty." };
    }
    return { id: drawer.id, valid: true, status: "Valid", patch: formatter };
  }

  try {
    const trimmed = drawer.content.trim();
    const patch = trimmed ? JSON.parse(trimmed) : {};
    return { id: drawer.id, valid: true, status: "Valid", patch };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Invalid JSON";
    return { id: drawer.id, valid: false, status: "Invalid JSON", error: message };
  }
}

export function safeDeepMergeOption(base: Record<string, unknown>, patch: Record<string, unknown>): Record<string, unknown> {
  const target = cloneValue(base);
  for (const [key, value] of Object.entries(patch)) {
    if (key === "__proto__" || key === "constructor" || key === "prototype") continue;
    const current = target[key];
    if (isRecord(current) && isRecord(value)) {
      target[key] = safeDeepMergeOption(current, value);
    } else {
      target[key] = cloneValue(value);
    }
  }
  return target;
}

export function applyCodeDrawersToOption(
  option: Record<string, unknown>,
  drawers: ChartCodeDrawerRecipe,
  context: CodeDrawerApplyContext
): CodeDrawerApplyResult {
  let next = cloneValue(option);
  const appliedDrawerIds: CodeDrawerId[] = [];
  const errors: Partial<Record<CodeDrawerId, string>> = {};
  void context;

  for (const id of DRAWER_APPLICATION_ORDER) {
    const drawer = drawers[id];
    if (!drawer) continue;
    const validation = validateCodeDrawer(drawer);
    if (!drawer.enabled) continue;
    if (!validation.valid) {
      errors[id] = validation.error ?? "Invalid JSON";
      continue;
    }
    try {
      next = applyDrawerPatch(next, drawer, validation.patch);
      appliedDrawerIds.push(id);
    } catch (error) {
      errors[id] = error instanceof Error ? error.message : "Drawer patch failed";
    }
  }

  return { option: next, appliedDrawerIds, errors };
}
