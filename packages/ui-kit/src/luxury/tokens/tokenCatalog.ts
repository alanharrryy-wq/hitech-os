import type { SemanticIntent, StyleId } from "../types.js";
import type {
  ElevationRamp,
  ElevationToken,
  GoldUsagePolicy,
  GlowBudget,
  LuxuryTokenPack,
  NeutralRamp,
  StrokeRamp,
  TexturePolicy
} from "./types.js";
import { SHARED_MOTION_BUDGET } from "./types.js";

type ElevationRow = readonly [liftPx: number, shadow: string, rim: string];
type SemanticRow = readonly [
  intent: SemanticIntent,
  primary: string,
  muted: string,
  glow: string,
  gradientStart?: string,
  gradientEnd?: string
];

interface TokenCatalogEntry {
  readonly neutral: NeutralRamp;
  readonly hairline: StrokeRamp;
  readonly innerStroke: StrokeRamp;
  readonly elevationRows: readonly [ElevationRow, ElevationRow, ElevationRow, ElevationRow];
  readonly semanticRows: readonly SemanticRow[];
  readonly glowBudget: GlowBudget;
  readonly goldUsage: GoldUsagePolicy;
  readonly texture: TexturePolicy;
}

function asElevationRamp(rows: TokenCatalogEntry["elevationRows"]): ElevationRamp {
  const ramp: Record<0 | 1 | 2 | 3, ElevationToken> = {
    0: {
      surfaceLift: `translateY(${rows[0][0]}px)`,
      shadow: rows[0][1],
      rimLight: rows[0][2]
    },
    1: {
      surfaceLift: `translateY(${rows[1][0]}px)`,
      shadow: rows[1][1],
      rimLight: rows[1][2]
    },
    2: {
      surfaceLift: `translateY(${rows[2][0]}px)`,
      shadow: rows[2][1],
      rimLight: rows[2][2]
    },
    3: {
      surfaceLift: `translateY(${rows[3][0]}px)`,
      shadow: rows[3][1],
      rimLight: rows[3][2]
    }
  };

  return ramp;
}

function buildSemanticRamp(styleId: StyleId, rows: readonly SemanticRow[]): LuxuryTokenPack["semantic"] {
  const defaultRow: SemanticRow = ["neutral", "hsl(210 16% 48%)", "hsl(210 24% 90%)", "hsl(210 22% 58% / 0.08)"];
  const rowMap = new Map<SemanticIntent, SemanticRow>();

  for (const row of rows) {
    rowMap.set(row[0], row);
  }

  const intents: readonly SemanticIntent[] = [
    "deal",
    "cash",
    "evidence",
    "outcome",
    "governance",
    "risk",
    "neutral"
  ];

  const result = {} as LuxuryTokenPack["semantic"];
  for (const intent of intents) {
    const row = rowMap.get(intent) ?? defaultRow;
    const entry = {
      primary: row[1],
      muted: row[2],
      glow: row[3]
    };

    if (styleId === "GRAPHITE_PRISM_ISO" && row[4] && row[5]) {
      result[intent] = {
        ...entry,
        chartGradientStart: row[4],
        chartGradientEnd: row[5]
      };
      continue;
    }

    result[intent] = entry;
  }

  return result;
}

const TOKEN_CATALOG: Readonly<Record<StyleId, TokenCatalogEntry>> = Object.freeze({
  LIQUID_GLASS: {
    neutral: {
      ink: "hsl(214 30% 18% / 0.9)",
      slate: "hsl(213 36% 88% / 0.36)",
      pearl: "hsl(214 60% 98% / 0.76)",
      panel: "linear-gradient(158deg, hsl(214 66% 98% / 0.76) 0%, hsl(217 40% 92% / 0.58) 100%)",
      panelRaised: "linear-gradient(164deg, hsl(214 72% 99% / 0.82) 0%, hsl(216 46% 94% / 0.66) 100%)",
      textStrong: "hsl(217 32% 13%)",
      textSoft: "hsl(214 18% 31%)"
    },
    hairline: {
      subtle: "hsl(213 56% 99% / 0.5)",
      strong: "hsl(216 40% 86% / 0.72)",
      widthPx: 1
    },
    innerStroke: {
      subtle: "hsl(212 88% 99% / 0.42)",
      strong: "hsl(214 78% 96% / 0.62)",
      widthPx: 1
    },
    elevationRows: [
      [0, "0 2px 8px hsl(216 40% 12% / 0.1)", "0 1px 0 hsl(214 90% 99% / 0.42) inset"],
      [-1, "0 12px 26px hsl(216 36% 10% / 0.14)", "0 1px 0 hsl(214 95% 99% / 0.48) inset"],
      [-2, "0 20px 44px hsl(216 32% 9% / 0.18)", "0 1px 0 hsl(214 98% 99% / 0.56) inset"],
      [-3, "0 28px 60px hsl(216 28% 8% / 0.22)", "0 1px 0 hsl(214 99% 99% / 0.64) inset"]
    ],
    semanticRows: [
      ["deal", "hsl(210 82% 54%)", "hsl(210 85% 93%)", "hsl(210 86% 64% / 0.18)"],
      ["cash", "hsl(152 68% 41%)", "hsl(152 58% 90%)", "hsl(152 72% 56% / 0.16)"],
      ["evidence", "hsl(198 86% 43%)", "hsl(198 78% 90%)", "hsl(198 88% 56% / 0.16)"],
      ["outcome", "hsl(224 78% 58%)", "hsl(224 82% 92%)", "hsl(224 82% 68% / 0.17)"],
      ["governance", "hsl(238 26% 44%)", "hsl(232 26% 90%)", "hsl(236 28% 66% / 0.14)"],
      ["risk", "hsl(8 74% 46%)", "hsl(8 82% 92%)", "hsl(8 80% 60% / 0.15)"],
      ["neutral", "hsl(216 20% 42%)", "hsl(216 34% 93%)", "hsl(216 30% 64% / 0.12)"]
    ],
    glowBudget: {
      maxAlpha: 0.18,
      maxBlurPx: 18,
      maxLayersPerSurface: 2
    },
    goldUsage: {
      enabled: false,
      maxCoverageRatio: 0,
      maxAccentsPerSurface: 0,
      allowTextFill: false,
      notes: ["Gold accents are disabled in LIQUID_GLASS."]
    },
    texture: {
      grainMaxOpacity: 0.035,
      gridMaxOpacity: 0.02,
      maxTextureLayers: 1
    }
  },
  GOLD_NOIR_TERMINAL: {
    neutral: {
      ink: "hsl(222 18% 12%)",
      slate: "hsl(223 14% 18%)",
      pearl: "hsl(38 34% 74% / 0.22)",
      panel: "linear-gradient(172deg, hsl(222 14% 14%) 0%, hsl(224 12% 10%) 100%)",
      panelRaised: "linear-gradient(172deg, hsl(222 14% 17%) 0%, hsl(224 12% 12%) 100%)",
      textStrong: "hsl(42 32% 90%)",
      textSoft: "hsl(42 18% 68%)"
    },
    hairline: {
      subtle: "hsl(42 42% 66% / 0.32)",
      strong: "hsl(42 58% 74% / 0.54)",
      widthPx: 1
    },
    innerStroke: {
      subtle: "hsl(42 32% 64% / 0.22)",
      strong: "hsl(42 48% 72% / 0.38)",
      widthPx: 1
    },
    elevationRows: [
      [0, "0 2px 10px hsl(224 22% 5% / 0.28)", "0 1px 0 hsl(42 24% 60% / 0.16) inset"],
      [-1, "0 14px 28px hsl(224 24% 4% / 0.36)", "0 1px 0 hsl(42 28% 62% / 0.2) inset"],
      [-2, "0 20px 44px hsl(224 28% 4% / 0.44)", "0 1px 0 hsl(42 32% 66% / 0.24) inset"],
      [-3, "0 26px 60px hsl(224 30% 3% / 0.5)", "0 1px 0 hsl(42 36% 70% / 0.3) inset"]
    ],
    semanticRows: [
      ["deal", "hsl(42 72% 64%)", "hsl(40 42% 20%)", "hsl(42 70% 60% / 0.08)"],
      ["cash", "hsl(149 44% 58%)", "hsl(148 34% 18%)", "hsl(150 56% 56% / 0.07)"],
      ["evidence", "hsl(199 48% 60%)", "hsl(199 38% 18%)", "hsl(199 58% 58% / 0.06)"],
      ["outcome", "hsl(43 68% 63%)", "hsl(41 42% 20%)", "hsl(43 70% 58% / 0.08)"],
      ["governance", "hsl(38 76% 68%)", "hsl(38 38% 20%)", "hsl(38 74% 66% / 0.08)"],
      ["risk", "hsl(8 64% 58%)", "hsl(8 40% 19%)", "hsl(8 68% 60% / 0.07)"],
      ["neutral", "hsl(42 36% 70%)", "hsl(42 30% 20%)", "hsl(42 42% 66% / 0.06)"]
    ],
    glowBudget: {
      maxAlpha: 0.08,
      maxBlurPx: 12,
      maxLayersPerSurface: 1
    },
    goldUsage: {
      enabled: true,
      maxCoverageRatio: 0.08,
      maxAccentsPerSurface: 2,
      allowTextFill: true,
      notes: [
        "Use gold for hairlines, key values, and governance markers only.",
        "Do not flood large surfaces with gold enamel."
      ]
    },
    texture: {
      grainMaxOpacity: 0.02,
      gridMaxOpacity: 0.012,
      maxTextureLayers: 1
    }
  },
  GRAPHITE_PRISM_ISO: {
    neutral: {
      ink: "hsl(214 20% 13%)",
      slate: "hsl(207 24% 21%)",
      pearl: "hsl(203 22% 78% / 0.18)",
      panel: "linear-gradient(168deg, hsl(211 24% 16%) 0%, hsl(204 30% 14%) 100%)",
      panelRaised: "linear-gradient(168deg, hsl(211 22% 18%) 0%, hsl(204 30% 15%) 100%)",
      textStrong: "hsl(196 24% 90%)",
      textSoft: "hsl(200 18% 70%)"
    },
    hairline: {
      subtle: "hsl(197 32% 68% / 0.24)",
      strong: "hsl(198 40% 74% / 0.38)",
      widthPx: 1
    },
    innerStroke: {
      subtle: "hsl(201 42% 64% / 0.2)",
      strong: "hsl(203 48% 70% / 0.32)",
      widthPx: 1
    },
    elevationRows: [
      [0, "0 4px 14px hsl(212 34% 7% / 0.3)", "0 1px 0 hsl(198 38% 76% / 0.14) inset"],
      [-1, "0 14px 32px hsl(212 38% 6% / 0.38)", "0 1px 0 hsl(198 42% 76% / 0.18) inset"],
      [-2, "0 22px 48px hsl(212 42% 5% / 0.44)", "0 1px 0 hsl(198 46% 78% / 0.22) inset"],
      [-3, "0 30px 66px hsl(212 46% 4% / 0.52)", "0 1px 0 hsl(198 50% 80% / 0.26) inset"]
    ],
    semanticRows: [
      ["deal", "hsl(198 78% 58%)", "hsl(198 44% 20%)", "hsl(198 80% 56% / 0.1)", "hsl(198 84% 60%)", "hsl(238 80% 68%)"],
      ["cash", "hsl(154 56% 54%)", "hsl(154 34% 20%)", "hsl(154 62% 52% / 0.09)", "hsl(154 64% 56%)", "hsl(192 72% 62%)"],
      ["evidence", "hsl(210 72% 62%)", "hsl(210 38% 22%)", "hsl(210 74% 60% / 0.09)", "hsl(210 78% 62%)", "hsl(258 76% 66%)"],
      ["outcome", "hsl(230 72% 66%)", "hsl(230 34% 24%)", "hsl(230 74% 64% / 0.1)", "hsl(230 76% 66%)", "hsl(284 72% 68%)"],
      ["governance", "hsl(188 38% 62%)", "hsl(188 24% 24%)", "hsl(188 44% 60% / 0.08)", "hsl(188 46% 62%)", "hsl(218 54% 64%)"],
      ["risk", "hsl(8 66% 58%)", "hsl(8 36% 22%)", "hsl(8 70% 60% / 0.1)", "hsl(8 70% 60%)", "hsl(332 64% 62%)"],
      ["neutral", "hsl(196 34% 66%)", "hsl(196 24% 24%)", "hsl(196 38% 64% / 0.08)", "hsl(196 44% 66%)", "hsl(228 48% 68%)"]
    ],
    glowBudget: {
      maxAlpha: 0.1,
      maxBlurPx: 14,
      maxLayersPerSurface: 1
    },
    goldUsage: {
      enabled: false,
      maxCoverageRatio: 0,
      maxAccentsPerSurface: 0,
      allowTextFill: false,
      notes: ["Gold accents are disabled in GRAPHITE_PRISM_ISO."]
    },
    texture: {
      grainMaxOpacity: 0.024,
      gridMaxOpacity: 0.03,
      maxTextureLayers: 1
    }
  }
});

export function buildTokenPackFromCatalog(styleId: StyleId): LuxuryTokenPack {
  const entry = TOKEN_CATALOG[styleId];

  return {
    styleId,
    neutral: entry.neutral,
    hairline: entry.hairline,
    innerStroke: entry.innerStroke,
    elevation: asElevationRamp(entry.elevationRows),
    semantic: buildSemanticRamp(styleId, entry.semanticRows),
    glowBudget: entry.glowBudget,
    goldUsage: entry.goldUsage,
    texture: entry.texture,
    motion: SHARED_MOTION_BUDGET
  };
}
