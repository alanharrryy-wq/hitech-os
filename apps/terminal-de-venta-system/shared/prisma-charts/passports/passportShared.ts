import type { PrismaChartPassport, PrismaChartVisualKnob } from "../prismaChartAtlas";

export const supportedStates = ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"];

export const commonDoNotTouch = [
  "Do not import ECharts outside shared/prisma-charts.",
  "Do not add React runtime aliases.",
  "Do not add client-side database access.",
  "Do not mark fallback data as real."
];

export function knob(name: string, purpose: string, safeRange: string, whereApplied: string, risk: string): PrismaChartVisualKnob {
  return { name, purpose, safeRange, whereApplied, risk };
}

export function editPlaybook(input: { visualRecipe: string; adapterName: string; contractType: string; componentFile: string; deckFile: string }): PrismaChartPassport["editPlaybook"] {
  return {
    visualEdit: [`shared/prisma-charts/recipes/${input.visualRecipe}.ts`, "shared/prisma-charts/prismaChartOptions.ts"],
    dataEdit: ["shared/prisma-charts/prismaChartAdapters.ts", input.adapterName],
    contractEdit: ["shared/prisma-charts/prismaChartContracts.ts", input.contractType, "tools/verify_prisma_chart_atlas_01.mjs"],
    layoutEdit: [input.deckFile, input.componentFile]
  };
}

export function validation(previewRoute: string): PrismaChartPassport["validation"] {
  return {
    previewRoute,
    expectedSelectors: ["[data-prisma-charts-enabled]", "article"],
    verifier: "pnpm run prisma:charts:atlas:verify",
    manualChecks: ["Open preview route manually if a visual capture is needed.", "Confirm partial/mock labels are honest."]
  };
}

export const commonAccessibility = {
  ariaLabel: "Chart has a semantic title and ECharts aria description.",
  textDescription: "Card footer reports source and confidence.",
  nonColorSignal: "Status appears in text, tooltip, or footer in addition to color.",
  keyboardFocus: "Route remains navigable without chart-only interaction."
};
