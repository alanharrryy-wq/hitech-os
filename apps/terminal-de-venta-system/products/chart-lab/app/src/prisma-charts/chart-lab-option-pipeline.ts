// PRISMA_CHART_LAB_OPTION_PIPELINE_V3
import { applyChartLabControls } from "./chart-lab-control-model";
import { applyTargetProfileToOption } from "./chart-lab-target-profiles";
import { resolveChartLabMotionPreset, resolveChartLabVisualPreset, resolveChartLabInteractionPreset } from "./chart-lab-power-presets";
import { applyChartLabAdvancedPatch } from "./chart-lab-advanced-patch";
import type { ChartLabRecipe } from "./chart-lab-recipe-model";
import type { LabChartControlState } from "./chart-lab-types";

function cloneOption(option: Record<string, unknown>): Record<string, unknown> {
  return JSON.parse(JSON.stringify(option)) as Record<string, unknown>;
}

function asRecords(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item)) : [];
}

export type ChartLabOptionPipelineInput = {
  chartId: string;
  baseOption: Record<string, unknown>;
  controls: LabChartControlState;
  recipe?: ChartLabRecipe;
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

  if (input.recipe?.advancedPatch && Object.keys(input.recipe.advancedPatch).length) {
    const patched = applyChartLabAdvancedPatch(controlled, input.recipe.advancedPatch);
    warnings.push(...patched.warnings, ...patched.errors);
    appliedLayers.push("advancedPatch");
    return { option: patched.option, warnings, appliedLayers };
  }

  return { option: controlled, warnings, appliedLayers };
}
