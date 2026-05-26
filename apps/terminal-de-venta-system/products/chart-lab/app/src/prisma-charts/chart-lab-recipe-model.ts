// PRISMA_CHART_LAB_RECIPE_MODEL_V3
import type { LabChartControlState, LabChartControlValue, LabChartPreviewFrame } from "./chart-lab-types";

export type ChartLabRecipeVersion = 3;
export type ChartLabTarget = LabChartPreviewFrame;
export type ChartLabPresetId = string;

export type ChartLabRecipeLayer = {
  visualPreset: ChartLabPresetId;
  motionPreset: ChartLabPresetId;
  interactionPreset: ChartLabPresetId;
  labelPreset: ChartLabPresetId;
  dataScenario: string;
  target: ChartLabTarget;
};

export type ChartLabRecipe = {
  recipeVersion: ChartLabRecipeVersion;
  chartId: string;
  title?: string;
  generatedAt: string;
  source: "prisma-chart-lab-power-studio";
  layers: ChartLabRecipeLayer;
  controls: LabChartControlState;
  manualOverrides: LabChartControlState;
  advancedPatch: Record<string, unknown>;
  guidedTourId?: string;
  notes?: string;
};

export type ChartLabRecipeValidation = {
  ok: boolean;
  warnings: string[];
  errors: string[];
};

export const CHART_LAB_RECIPE_VERSION: ChartLabRecipeVersion = 3;

function safeRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function safeControls(value: unknown): LabChartControlState {
  const record = safeRecord(value);
  const next: LabChartControlState = {};
  for (const [key, raw] of Object.entries(record)) {
    if (typeof raw === "string" || typeof raw === "number" || typeof raw === "boolean") next[key] = raw;
    else if (Array.isArray(raw) && raw.every((item) => typeof item === "string")) next[key] = raw;
  }
  return next;
}

export function createChartLabRecipe(input: {
  chartId: string;
  title?: string;
  target: ChartLabTarget;
  controls: LabChartControlState;
  visualPreset?: string;
  motionPreset?: string;
  interactionPreset?: string;
  labelPreset?: string;
  dataScenario?: string;
  manualOverrides?: LabChartControlState;
  advancedPatch?: Record<string, unknown>;
  guidedTourId?: string;
  notes?: string;
}): ChartLabRecipe {
  return {
    recipeVersion: CHART_LAB_RECIPE_VERSION,
    chartId: input.chartId,
    title: input.title,
    generatedAt: new Date().toISOString(),
    source: "prisma-chart-lab-power-studio",
    layers: {
      target: input.target,
      visualPreset: input.visualPreset ?? String(input.controls.themePreset ?? "crystal-ops"),
      motionPreset: input.motionPreset ?? String(input.controls.motionPreset ?? input.controls.motionMode ?? "subtle-premium"),
      interactionPreset: input.interactionPreset ?? String(input.controls.interactionPreset ?? "explore"),
      labelPreset: input.labelPreset ?? String(input.controls.labelPreset ?? "smart-hotspots"),
      dataScenario: input.dataScenario ?? String(input.controls.dataScenario ?? "clean")
    },
    controls: { ...input.controls },
    manualOverrides: { ...(input.manualOverrides ?? {}) },
    advancedPatch: { ...(input.advancedPatch ?? {}) },
    guidedTourId: input.guidedTourId,
    notes: input.notes
  };
}

export function serializeChartLabRecipe(recipe: ChartLabRecipe): string {
  return JSON.stringify(recipe, null, 2);
}

export function parseChartLabRecipe(raw: string): ChartLabRecipe {
  const parsed = JSON.parse(raw) as Record<string, unknown>;
  const layers = safeRecord(parsed.layers);
  return {
    recipeVersion: CHART_LAB_RECIPE_VERSION,
    chartId: String(parsed.chartId ?? ""),
    title: typeof parsed.title === "string" ? parsed.title : undefined,
    generatedAt: typeof parsed.generatedAt === "string" ? parsed.generatedAt : new Date().toISOString(),
    source: "prisma-chart-lab-power-studio",
    layers: {
      target: layers.target === "tablet" || layers.target === "mobile" ? layers.target : "pc",
      visualPreset: String(layers.visualPreset ?? "crystal-ops"),
      motionPreset: String(layers.motionPreset ?? "subtle-premium"),
      interactionPreset: String(layers.interactionPreset ?? "explore"),
      labelPreset: String(layers.labelPreset ?? "smart-hotspots"),
      dataScenario: String(layers.dataScenario ?? "clean")
    },
    controls: safeControls(parsed.controls),
    manualOverrides: safeControls(parsed.manualOverrides),
    advancedPatch: safeRecord(parsed.advancedPatch),
    guidedTourId: typeof parsed.guidedTourId === "string" ? parsed.guidedTourId : undefined,
    notes: typeof parsed.notes === "string" ? parsed.notes : undefined
  };
}

export function validateChartLabRecipe(recipe: ChartLabRecipe): ChartLabRecipeValidation {
  const errors: string[] = [];
  const warnings: string[] = [];
  if (recipe.recipeVersion !== CHART_LAB_RECIPE_VERSION) errors.push(`Unsupported recipeVersion: ${recipe.recipeVersion}`);
  if (!recipe.chartId) errors.push("Missing chartId");
  if (!["pc", "tablet", "mobile"].includes(recipe.layers.target)) errors.push(`Invalid target: ${recipe.layers.target}`);
  if (!Object.keys(recipe.controls).length) warnings.push("Recipe has no controls; this may be an untouched base chart.");
  return { ok: errors.length === 0, warnings, errors };
}

export function roundTripChartLabRecipe(recipe: ChartLabRecipe): ChartLabRecipeValidation {
  const parsed = parseChartLabRecipe(serializeChartLabRecipe(recipe));
  const validation = validateChartLabRecipe(parsed);
  if (parsed.chartId !== recipe.chartId) validation.errors.push("Roundtrip chartId mismatch");
  if (parsed.layers.target !== recipe.layers.target) validation.errors.push("Roundtrip target mismatch");
  return { ...validation, ok: validation.errors.length === 0 };
}

export function changedControlsFromDefaults(controls: LabChartControlState, defaults: LabChartControlState): string[] {
  return Object.keys(controls).filter((key) => JSON.stringify(controls[key] as LabChartControlValue) !== JSON.stringify(defaults[key] as LabChartControlValue));
}
