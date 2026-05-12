export type PrismaChartIntentMapping = {
  phrase: string;
  chartId?: string;
  family?: string;
  editType: "visual" | "data" | "contract" | "layout" | "lab";
  files: string[];
  knobs: string[];
  doNotTouch: string[];
};

export const prismaChartIntentDictionary: PrismaChartIntentMapping[] = [
  {
    phrase: "haz el radar mas premium",
    chartId: "mobile.health-radar-compact",
    family: "radar",
    editType: "visual",
    files: ["shared/prisma-charts/recipes/radarRecipe.ts", "shared/prisma-charts/prismaChartOptions.ts"],
    knobs: ["lineWidth", "areaFillOpacity", "splitAreaOpacity", "axisNameWeight", "pointGlow"],
    doNotTouch: ["shared/prisma-charts/prismaChartAdapters.ts", "products/mobile/app/tsconfig.json", "shared/prisma-charts/prismaEchartsLoader.ts"]
  },
  {
    phrase: "la grafica de frescura se ve equis",
    chartId: "mobile.freshness-beacon-grid",
    family: "rings",
    editType: "visual",
    files: ["shared/prisma-charts/recipes/ringsRecipe.ts", "shared/prisma-charts/prismaChartOptions.ts"],
    knobs: ["ringThickness", "ringGap", "statusPalette", "centerLabelSize", "staleEmphasis"],
    doNotTouch: ["Mobile snapshot adapter", "React runtime aliases"]
  },
  {
    phrase: "el waterfall debe verse mas ejecutivo",
    chartId: "pc.financial-operational-waterfall",
    family: "waterfall",
    editType: "visual",
    files: ["shared/prisma-charts/recipes/waterfallRecipe.ts", "shared/prisma-charts/prismaChartOptions.ts"],
    knobs: ["connectorStyle", "totalBarEmphasis", "labelFormatter", "valueDensity"],
    doNotTouch: ["PC dashboard query", "Prisma schema"]
  },
  {
    phrase: "la grafica esta mostrando datos falsos",
    editType: "data",
    files: ["shared/prisma-charts/prismaChartAdapters.ts", "shared/prisma-charts/prismaChartQuality.ts", "docs/prisma/PRISMA_CHART_REAL_DATA_SOURCE_MAP.md"],
    knobs: [],
    doNotTouch: ["visual recipes", "CSS", "React runtime aliases"]
  },
  {
    phrase: "quiero moverla a Mobile",
    editType: "layout",
    files: ["shared/prisma-charts/prismaChartAtlas.ts", "shared/prisma-charts/passports/*.passport.ts", "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx"],
    knobs: ["surfaceProfile", "labelDensity", "tooltipDensity"],
    doNotTouch: ["original adapter contract", "client DB access"]
  },
  {
    phrase: "quiero verla junto con todas",
    editType: "lab",
    files: ["products/pc/app/app/prisma-insights/chart-lab/page.tsx", "shared/prisma-charts/prismaChartAtlas.ts"],
    knobs: [],
    doNotTouch: ["production flags"]
  }
];

export function findChartIntent(phrase: string) {
  const normalized = phrase.trim().toLowerCase();
  return prismaChartIntentDictionary.find((intent) => intent.phrase === normalized) ?? null;
}
