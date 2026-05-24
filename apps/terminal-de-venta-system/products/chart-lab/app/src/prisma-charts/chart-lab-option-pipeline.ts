// PRISMA_CHART_LAB_OPTION_PIPELINE_V3
import { applyChartLabControls } from "./chart-lab-control-model";
import { applyTargetProfileToOption } from "./chart-lab-target-profiles";
import { getVisualPresetVisibilityFloor, resolveChartLabMotionPreset, resolveChartLabVisualPreset, resolveChartLabInteractionPreset } from "./chart-lab-power-presets";
import { applyChartLabAdvancedPatch } from "./chart-lab-advanced-patch";
import { applyCodeDrawersToOption, type ChartCodeDrawerRecipe } from "./chart-lab-code-drawers";
import type { ChartLabRecipe } from "./chart-lab-recipe-model";
import type { LabChartControlState } from "./chart-lab-types";

function cloneOption(option: Record<string, unknown>): Record<string, unknown> {
  return JSON.parse(JSON.stringify(option)) as Record<string, unknown>;
}

function asRecords(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item)) : [];
}

type VisibilityFloor = {
  minSeriesOpacity: number;
  minLineOpacity: number;
  minAreaOpacity: number;
  minLabelContrast: number;
};

const DEFAULT_VISIBILITY_FLOOR: VisibilityFloor = {
  minSeriesOpacity: 0.38,
  minLineOpacity: 0.48,
  minAreaOpacity: 0.18,
  minLabelContrast: 0.74
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function ensureRecord(parent: Record<string, unknown>, key: string): Record<string, unknown> {
  const existing = parent[key];
  if (isRecord(existing)) return existing;
  const next: Record<string, unknown> = {};
  parent[key] = next;
  return next;
}

function raiseOpacity(target: Record<string, unknown>, key: string, minimum: number) {
  const current = target[key];
  if (typeof current === "number" && Number.isFinite(current) && current < minimum) target[key] = minimum;
}

function raiseStyleOpacity(series: Record<string, unknown>, key: "itemStyle" | "lineStyle" | "areaStyle", minimum: number) {
  const style = series[key];
  if (isRecord(style)) raiseOpacity(style, "opacity", minimum);
}

function raiseNestedStyleOpacity(parent: Record<string, unknown>, key: "itemStyle" | "lineStyle" | "areaStyle", minimum: number) {
  const style = parent[key];
  if (isRecord(style)) raiseOpacity(style, "opacity", minimum);
}

function normalizeSeries(option: Record<string, unknown>): Record<string, unknown>[] {
  const series = option.series;
  if (Array.isArray(series)) return series.filter(isRecord);
  return isRecord(series) ? [series] : [];
}

export function applyChartLabVisibilityGuard(option: Record<string, unknown>, floor: VisibilityFloor = DEFAULT_VISIBILITY_FLOOR): Record<string, unknown> {
  const guarded = cloneOption(option);
  for (const series of normalizeSeries(guarded)) {
    const type = typeof series.type === "string" ? series.type : "";
    raiseOpacity(series, "opacity", floor.minSeriesOpacity);
    raiseStyleOpacity(series, "itemStyle", floor.minSeriesOpacity);
    raiseStyleOpacity(series, "lineStyle", type === "sankey" ? 0.52 : floor.minLineOpacity);
    raiseStyleOpacity(series, "areaStyle", floor.minAreaOpacity);

    if (type === "sankey") {
      const itemStyle = ensureRecord(series, "itemStyle");
      if (typeof itemStyle.borderWidth !== "number" || itemStyle.borderWidth < 1) itemStyle.borderWidth = 1;
      const label = series.label;
      if (isRecord(label)) raiseOpacity(label, "opacity", floor.minLabelContrast);
    }

    if (type === "heatmap") {
      const emphasis = series.emphasis;
      if (isRecord(emphasis)) {
        raiseNestedStyleOpacity(emphasis, "itemStyle", floor.minSeriesOpacity);
        const label = emphasis.label;
        if (isRecord(label)) raiseOpacity(label, "opacity", floor.minLabelContrast);
      }
    }

    if (type === "graph" || type === "sankey" || type === "line") {
      const blur = series.blur;
      if (isRecord(blur)) {
        raiseNestedStyleOpacity(blur, "itemStyle", 0.24);
        raiseNestedStyleOpacity(blur, "lineStyle", 0.3);
        raiseNestedStyleOpacity(blur, "areaStyle", floor.minAreaOpacity);
      }
    }
  }
  return guarded;
}

export type ChartLabOptionPipelineInput = {
  chartId: string;
  baseOption: Record<string, unknown>;
  controls: LabChartControlState;
  recipe?: ChartLabRecipe;
  codeDrawers?: ChartCodeDrawerRecipe;
  reducedMotion: boolean;
};

export type ChartLabOptionPipelineResult = {
  option: Record<string, unknown>;
  warnings: string[];
  appliedLayers: string[];
};

export function buildChartLabOption(input: ChartLabOptionPipelineInput): ChartLabOptionPipelineResult {
  const option = cloneOption(input.baseOption);
  const warnings: string[] = [];
  const appliedLayers: string[] = [];
  const target = input.recipe?.layers.target ?? "pc";
  const visualPreset = resolveChartLabVisualPreset(input.recipe?.layers.visualPreset ?? String(input.controls.themePreset ?? "crystal-ops"));
  const motionPreset = resolveChartLabMotionPreset(input.recipe?.layers.motionPreset ?? String(input.controls.motionPreset ?? input.controls.motionMode ?? "subtle-premium"));
  const interactionPreset = resolveChartLabInteractionPreset(input.recipe?.layers.interactionPreset ?? String(input.controls.interactionPreset ?? "explore"));

  option.color = visualPreset.palette;
  option.backgroundColor = visualPreset.background;
  option.animation = !input.reducedMotion && motionPreset.animation;
  option.animationDuration = motionPreset.duration;
  option.animationDurationUpdate = motionPreset.updateDuration;
  option.animationEasing = motionPreset.easing;
  option.animationEasingUpdate = motionPreset.easing;
  for (const series of asRecords(option.series)) {
    if (motionPreset.universalTransition !== "off") series.universalTransition = motionPreset.universalTransition === "full";
    const emphasis = (series.emphasis && typeof series.emphasis === "object" ? series.emphasis : {}) as Record<string, unknown>;
    emphasis.focus = interactionPreset.hoverSpotlight === "off" ? "none" : "series";
    series.emphasis = emphasis;
  }
  appliedLayers.push("visualPreset", "motionPreset", "interactionPreset");

  const controlled = applyChartLabControls({ chartId: input.chartId, option, values: input.controls, reducedMotion: input.reducedMotion });
  appliedLayers.push("manualControls");
  applyTargetProfileToOption(controlled, target);
  appliedLayers.push(`target:${target}`);

  let finalOption = controlled;
  if (input.recipe?.advancedPatch && Object.keys(input.recipe.advancedPatch).length) {
    const patched = applyChartLabAdvancedPatch(controlled, input.recipe.advancedPatch);
    warnings.push(...patched.warnings, ...patched.errors);
    appliedLayers.push("advancedPatch");
    finalOption = patched.option;
  }

  if (input.codeDrawers) {
    const drawerResult = applyCodeDrawersToOption(finalOption, input.codeDrawers, { chartId: input.chartId });
    warnings.push(...Object.entries(drawerResult.errors).map(([drawerId, message]) => `${drawerId}: ${message}`));
    appliedLayers.push(...drawerResult.appliedDrawerIds.map((drawerId) => `codeDrawer:${drawerId}`));
    finalOption = drawerResult.option;
  }

  const guarded = applyChartLabVisibilityGuard(finalOption, getVisualPresetVisibilityFloor(visualPreset.id));
  appliedLayers.push("visibilityGuard");
  return { option: guarded, warnings, appliedLayers };
}
