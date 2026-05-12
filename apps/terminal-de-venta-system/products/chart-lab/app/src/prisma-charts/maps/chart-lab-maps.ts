import { chartLabRegistry, chartOpsChartIds } from "../chart-lab-registry";
import { chartControlSchemas } from "../chart-lab-control-model";

export const chartLabGeneratedAt = "2026-05-12T00:00:00.000-06:00";
export const chartLabLocalRoute = "LOCAL_CHART_LAB_PORT_3000";
export const chartLabPagesProject = "prisma-chart-lab";
export const chartLabPagesPlaceholder = "https://prisma-chart-lab.pages.dev/";
export const chartLabTunnelHostnamePlaceholder = "prisma-chart-lab-preview.example.com";

const chartOpsEntries = chartLabRegistry.filter((chart) => chartOpsChartIds.includes(chart.id as (typeof chartOpsChartIds)[number]));

function titleCase(value: string) {
  return value
    .split(/[-_.\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function surfaceRole(surface: string) {
  if (surface === "pc") return "PC governs; detail-rich, audit-friendly, feature-flagged.";
  if (surface === "tablet") return "Tablet operates; touch-first, offline-aware, never executive analytics.";
  if (surface === "mobile") return "Mobile supervises; compact, read-only, evidence-first.";
  return "Web is public/demo-safe and mock-only unless explicitly approved.";
}

export const chartAtlasMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  title: chart.title,
  family: chart.family,
  surface: chart.surface,
  component: chart.componentPath,
  optionBuilder: chart.optionBuilderName ?? "component-owned",
  contract: `shared/prisma-charts/prismaChartContracts.ts#${chart.chartType}`,
  adapter: chart.optionBuilderName ? `shared/prisma-charts/prismaChartAdapters.ts#${chart.optionBuilderName.replace("Option", "ViewModel")}` : "unavailable",
  mock: chart.mockPath,
  route: chartLabLocalRoute,
  status: chart.readiness
}));

export const dataSourceMap = chartOpsEntries.map((chart) => {
  const safeSurface = chart.surface === "tablet" || chart.id.startsWith("mobile.action") || chart.id.startsWith("mobile.health") || chart.id.startsWith("mobile.freshness") || chart.id.startsWith("mobile.confidence");
  return {
    chartId: chart.id,
    classification: safeSurface ? "safe" : "partial",
    candidateSource:
      chart.surface === "pc"
        ? "PC dashboard, tri-db bridge status, canonical Prisma/API adapters"
        : chart.surface === "tablet"
          ? "Tablet runtime snapshot and outbox summaries"
          : "Mobile data-plane snapshot and read-only intelligence APIs",
    adapterPlan: chart.optionBuilderName ? `Build real/partial data through ${chart.optionBuilderName.replace("Option", "ViewModel")} adapter, never client DB access.` : "Create adapter before production promotion.",
    missingGaps: safeSurface ? ["historical depth may still be partial"] : ["canonical real source coverage is partial", "fallback must stay labeled mock/demo"],
    fallbackPolicy: "Deterministic mock fallback allowed only when surfaced as mock/demo or partial.",
    realCoverageStatus: safeSurface ? "safe-partial" : "partial"
  };
});

export const runtimeControlMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  controls: (chartControlSchemas[chart.id] ?? []).map((control) => ({
    controlId: control.id,
    type: control.type,
    default: control.defaultValue,
    current: control.defaultValue,
    affectedOptionPath: control.affectedOptionPath ?? null,
    affectedDataPath: control.affectedDataTransform ?? null,
    validationRule: control.validation,
    resetBehavior: control.resetBehavior
  }))
}));

export const visualKnobMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  visualKnobs: (chartControlSchemas[chart.id] ?? [])
    .filter((control) => control.affectedLayer !== "data")
    .map((control) => ({
      name: control.id,
      safeRange: control.min !== undefined && control.max !== undefined ? `${control.min}-${control.max}` : "schema options",
      premiumValue: control.defaultValue,
      risk: control.risk,
      affectedLayer: control.affectedLayer,
      performanceImpact: control.id.includes("animation") ? "motion cost; disabled by reduced motion" : "low",
      accessibilityImpact: control.id.includes("showLabels") ? "labels provide non-color signal" : "must preserve text summary"
    }))
}));

export const visualRecipeMap = [
  "flow",
  "density",
  "network",
  "treemap",
  "timeline",
  "waterfall",
  "strip",
  "matrix",
  "stack",
  "radar",
  "rings",
  "sparks",
  "bands"
].map((family) => ({
  family,
  recipe: `${family}Recipe`,
  defaultTokens: ["prismaChartTokens", "statusColor", "severityColor"],
  surfaceOverrides: {
    pc: "wide, audit-friendly labels, rich tooltip",
    tablet: "touch-first, high contrast, low-cognitive-load",
    mobile: "compact, read-only, evidence-first",
    web: "public-safe, mock/demo only"
  },
  stateOverrides: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  tooltip: family === "sparks" ? "compact" : family === "flow" || family === "network" ? "rich" : "standard",
  motion: family === "network" || family === "flow" ? "safe" : "subtle"
}));

export const stateGalleryMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  family: chart.family,
  states: {
    happy: "Data is present, fresh, and high-confidence.",
    empty: "No records exist for the selected scope; render an honest empty state.",
    partial: "Some safe sources are present but coverage is incomplete.",
    stale: "At least one source is older than the accepted freshness window.",
    offline: "A source is unreachable; do not hide missing coverage.",
    unknown: "The adapter cannot determine state safely.",
    dense: "Many records are present; reduce labels before reducing truth.",
    critical: "Evidence-backed severity only; no invented urgent state."
  }
}));

export const humanIntentMap = [
  {
    phrase: "haz la grafica mas premium",
    chartId: null,
    family: "any",
    editType: "visual",
    files: ["shared/prisma-charts/recipes/*Recipe.ts", "shared/prisma-charts/prismaChartOptions.ts", "products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts"],
    knobs: ["themePreset", "visualIntensity", "showLabels"],
    validation: ["pnpm run chart-lab:verify:controls", "pnpm run prisma:echarts:verify"]
  },
  {
    phrase: "sube la evidencia del flujo causal",
    chartId: "pc.causal-flow-ribbon",
    family: "flow",
    editType: "controls",
    files: ["products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts", "shared/prisma-charts/prismaChartOptions.ts"],
    knobs: ["evidenceMode", "detailLevel", "confidenceFloor"],
    validation: ["pnpm run chart-lab:verify:controls"]
  },
  {
    phrase: "quiero mover esta grafica a mobile",
    chartId: null,
    family: "any",
    editType: "promotion",
    files: ["products/chart-lab/app/src/prisma-charts/maps/chart-lab-maps.ts", "products/chart-lab/app/scripts/promote-chart.mjs"],
    knobs: ["surfaceTransport", "featureFlag", "viewportProfile"],
    validation: ["pnpm run chart-lab:promote -- --chart=<chartId> --target=mobile --dry-run"]
  },
  {
    phrase: "la grafica muestra datos falsos",
    chartId: null,
    family: "any",
    editType: "data",
    files: ["docs/prisma/PRISMA_CHART_REAL_DATA_SOURCE_MAP.md", "shared/prisma-charts/prismaChartAdapters.ts"],
    knobs: ["dataScenario", "fallbackPolicy"],
    validation: ["pnpm run chart-lab:verify:maps", "pnpm run chart-lab:verify:no-leaks"]
  }
];

export const surfaceTransportMap = chartOpsEntries.map((chart) => {
  const validTargets = chart.surface === "pc" ? ["pc", "web"] : chart.surface === "tablet" ? ["tablet", "web"] : ["mobile", "web"];
  return {
    chartId: chart.id,
    validTargets,
    surfaceProfile: surfaceRole(chart.surface),
    unsafeTargets: ["pc", "tablet", "mobile", "web"].filter((target) => !validTargets.includes(target)).map((target) => ({
      target,
      reason:
        target === "tablet"
          ? "Tablet must stay operational, touch-first, and not executive analytics."
          : target === "pc"
            ? "PC governs and must not become POS."
            : target === "mobile"
              ? "Mobile supervises and must remain read-only."
              : "Web must be public/demo-safe."
    })),
    requiredFeatureFlag: `PRISMA_CHART_${chart.id.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_PREVIEW`,
    targetWrapperPattern: `${titleCase(chart.surface)}ChartPreviewWrapper with feature flag off by default`
  };
});

export const promotionManifestMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  sourceFiles: [
    chart.componentPath,
    chart.mockPath,
    "shared/prisma-charts/prismaChartOptions.ts",
    "shared/prisma-charts/prismaChartContracts.ts",
    "shared/prisma-charts/prismaChartAdapters.ts"
  ],
  targetFiles: {
    pc: [`products/pc/app/app/prisma-insights/charts/${titleCase(chart.shortName).replace(/\s+/g, "")}.tsx`],
    tablet: [`products/tablet/app/app/prisma-charts/${titleCase(chart.shortName).replace(/\s+/g, "")}.tsx`],
    mobile: [`products/mobile/app/app/prisma-charts/${titleCase(chart.shortName).replace(/\s+/g, "")}.tsx`],
    web: [`products/chart-lab/app/out/${chart.id}/index.html`]
  },
  dependencies: ["shared/prisma-charts", "feature flag", "surface wrapper"],
  flags: [`PRISMA_CHART_${chart.id.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_PREVIEW=false`],
  backups: "Apply creates tools/_local/backups/chart-promotion/<timestamp>/manifest.json before writing.",
  validationCommands: [
    "pnpm -C products/chart-lab/app verify:promotion",
    `pnpm -C products/chart-lab/app promote -- --chart=${chart.id} --target=${chart.surface} --dry-run`
  ],
  rollbackNotes: "Rollback manifest records source/target pairs; restore backup files before re-running target validation."
}));

export const routeMap = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  localLabRoute: chartLabLocalRoute,
  productPreviewRoute:
    chart.surface === "pc" ? "/prisma-insights?preview=charts" : chart.surface === "tablet" ? "/pos?charts=preview" : "/prisma-app?charts=preview",
  productProductionRoute: chart.surface === "pc" ? "/prisma-insights" : chart.surface === "tablet" ? "/pos" : "/prisma-app",
  cloudflarePagesUrl: `${chartLabPagesPlaceholder}#${chart.id}`,
  tunnelHostname: `https://${chartLabTunnelHostnamePlaceholder}/#${chart.id}`
}));

export const dependencyImportMap = {
  echartsImportBoundary: "Only products/chart-lab/app and shared/prisma-charts/PrismaEChart.tsx may resolve ECharts directly.",
  sharedChartImports: ["shared/prisma-charts/prismaChartContracts.ts", "shared/prisma-charts/prismaChartOptions.ts", "shared/prisma-charts/prismaChartMocks.ts"],
  forbiddenImports: ["client-side database access", "environment files", "lab shell inside product apps", "React runtime aliases"],
  productAppDependencies: "Product surfaces must use shared chart contracts/adapters/wrappers, not lab-only code.",
  labOnlyDependencies: ["wrangler", "Next static export scripts", "Cloudflare tunnel scripts"]
};

export const cloudflareExposureMap = {
  publicAssets: "products/chart-lab/app/out",
  hostname: chartLabTunnelHostnamePlaceholder,
  deploymentMode: "Cloudflare Pages static export",
  tunnelMode: "cloudflared token or local-config mode to the local Chart Lab port with final http_status:404 fallback",
  sensitiveStringsDenied: ["Windows absolute drive paths", "database URL env vars", "env file contents", "Cloudflare token names/values", "cloudflared credentials", "local diagnostics"],
  diagnosticsVisibility: "Public build exposes only public-safe health badges and mock/demo labels."
};

export const validationMap = {
  chartVerifier: "pnpm -C products/chart-lab/app verify",
  labVerifier: "pnpm -C products/chart-lab/app verify:all",
  controlsVerifier: "pnpm -C products/chart-lab/app verify:controls",
  passportVerifier: "pnpm -C products/chart-lab/app verify:passports",
  cloudflareVerifier: "pnpm -C products/chart-lab/app verify:cloudflare",
  promotionVerifier: "pnpm -C products/chart-lab/app verify:promotion",
  noLeakVerifier: "pnpm -C products/chart-lab/app verify:no-leaks",
  echartsBoundaryVerifier: "pnpm -C products/chart-lab/app verify:echarts-boundary"
};

export const handoffZipMap = {
  includes: [
    "products/chart-lab/app",
    "products/chart-lab/app/src",
    "products/chart-lab/app/app",
    "products/chart-lab/app/scripts",
    "products/chart-lab/app/docs",
    "products/chart-lab/app/deploy",
    "docs/prisma",
    "shared/prisma-charts"
  ],
  metadata: ["generatedAt", "chartIds", "hashes", "validationReport", "publicSafePolicy"],
  hashes: "sha256 for included source/docs files",
  docs: ["PRISMA_CHART_LAB_HANDOFF_PACK.md", "PRISMA_CHART_LAB_MAPS.md"],
  validationReport: "tools/_local/evidence/chart-lab/handoff-pack/latest-report.json"
};

export const visualTuningPassports = chartOpsEntries.map((chart) => ({
  chartId: chart.id,
  displayName: chart.title,
  questionAnswered: chart.operationalQuestion,
  family: chart.family,
  surface: chart.surface,
  primaryUser: chart.surface === "pc" ? "manager" : chart.surface === "tablet" ? "operator" : "owner",
  contract: `shared/prisma-charts/prismaChartContracts.ts#${chart.chartType}`,
  adapter: chart.optionBuilderName ? `shared/prisma-charts/prismaChartAdapters.ts#${chart.optionBuilderName.replace("Option", "ViewModel")}` : "unavailable",
  mock: chart.mockPath,
  optionBuilder: chart.optionBuilderName ?? "component-owned",
  visualRecipe: `${chart.family}Recipe`,
  visualKnobs: (chartControlSchemas[chart.id] ?? []).map((control) => ({
    name: control.id,
    label: control.label,
    purpose: control.affectedDataTransform ?? control.affectedOptionPath ?? control.affectedLayer,
    safeRange: control.min !== undefined && control.max !== undefined ? `${control.min}-${control.max}` : "enumerated schema values",
    defaultValue: control.defaultValue,
    premiumValue: control.defaultValue,
    min: control.min ?? null,
    max: control.max ?? null,
    step: control.step ?? null,
    unit: control.type === "range" ? "schema units" : null,
    riskLevel: control.risk,
    surfaceSuitability: surfaceRole(chart.surface),
    accessibilityImpact: control.id === "showLabels" ? "must preserve non-color text signal" : "must preserve summary and keyboard path",
    performanceImpact: control.id === "animation" ? "motion cost, reduced-motion disables it" : "low",
    promotionStatus: "lab-governed; feature flag off by default in product surfaces",
    affectedLayer: control.affectedLayer,
    whereApplied: control.affectedOptionPath ?? control.affectedDataTransform ?? "lab option transform",
    beforeAfterDescription: `Changing ${control.label} changes the rendered ${chart.title} preview, not only metadata.`,
    failureMode: "Invalid value is rejected by verifier or reset to default.",
    validationHint: control.validation
  })),
  runtimeControls: chartControlSchemas[chart.id] ?? [],
  states: ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"],
  interactions: ["hover tooltip", "keyboard navigation", "reset", "copy config"],
  accessibility: {
    ariaLabel: `${chart.title} answers ${chart.operationalQuestion}`,
    keyboard: "Chart list, tabs, controls, copy, and reset actions are buttons/inputs.",
    nonColorSignal: "Status is shown as text in inspector, state gallery, and config JSON."
  },
  knownRisks: dataSourceMap.find((item) => item.chartId === chart.id)?.missingGaps ?? [],
  doNotTouch: ["PC must not become POS", "Tablet must keep local-sale autonomy", "Mobile must remain read-only", "Control clean score stays text-only"],
  editPlaybook: ["Change schema", "Adjust option transform", "Update map/passport", "Run verify:controls and verify:maps"],
  validation: validationMap
}));

export const chartLabMapCatalog = {
  chartAtlasMap,
  dataSourceMap,
  runtimeControlMap,
  visualKnobMap,
  visualRecipeMap,
  stateGalleryMap,
  humanIntentMap,
  surfaceTransportMap,
  promotionManifestMap,
  routeMap,
  dependencyImportMap,
  cloudflareExposureMap,
  validationMap,
  handoffZipMap
} as const;

export type ChartLabMapName = keyof typeof chartLabMapCatalog;
