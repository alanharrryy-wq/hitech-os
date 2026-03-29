import type { AccentUsageSnapshot, MotionLevel, PerfProfile, SemanticIntent, StyleId, SurfaceId } from "./types.js";

export interface StyleScenario {
  readonly styleId: StyleId;
  readonly surfaceId: SurfaceId;
  readonly perfProfile: PerfProfile;
  readonly motionLevel: MotionLevel;
}

export const STYLE_SCENARIOS: readonly StyleScenario[] = [
  {
    styleId: "LIQUID_GLASS",
    surfaceId: "pitchCard",
    perfProfile: "default",
    motionLevel: "micro"
  },
  {
    styleId: "LIQUID_GLASS",
    surfaceId: "drawer",
    perfProfile: "perf",
    motionLevel: "off"
  },
  {
    styleId: "GOLD_NOIR_TERMINAL",
    surfaceId: "controlRoomHud",
    perfProfile: "default",
    motionLevel: "hero"
  },
  {
    styleId: "GOLD_NOIR_TERMINAL",
    surfaceId: "tableDense",
    perfProfile: "perf",
    motionLevel: "standard"
  },
  {
    styleId: "GRAPHITE_PRISM_ISO",
    surfaceId: "kpiWidget",
    perfProfile: "default",
    motionLevel: "micro"
  },
  {
    styleId: "GRAPHITE_PRISM_ISO",
    surfaceId: "rail",
    perfProfile: "perf",
    motionLevel: "off"
  }
];

export const ACCENT_SCENARIOS: readonly AccentUsageSnapshot[] = [
  {
    screenAccents: ["deal", "cash", "risk"],
    chartAccents: ["deal", "outcome", "risk"]
  },
  {
    screenAccents: ["governance", "evidence", "neutral", "cash"],
    chartAccents: ["deal", "cash", "evidence", "outcome", "risk"]
  },
  {
    screenAccents: ["neutral"],
    chartAccents: ["neutral"]
  }
];

export const SEMANTIC_INTENT_MATRIX: readonly SemanticIntent[] = [
  "deal",
  "cash",
  "evidence",
  "outcome",
  "governance",
  "risk",
  "neutral"
];

export const QUERY_FIXTURES = Object.freeze([
  {
    input: {
      luxStyle: "LIQUID_GLASS",
      luxSurface: "pitchCard",
      luxPerf: "default",
      luxMotion: "micro"
    },
    expected: "luxStyle=LIQUID_GLASS&luxSurface=pitchCard&luxPerf=default&luxMotion=micro"
  },
  {
    input: {
      luxStyle: "GRAPHITE_PRISM_ISO",
      luxSurface: "kpiWidget",
      luxPerf: "perf",
      luxMotion: "off",
      debug: "1"
    },
    expected: "luxStyle=GRAPHITE_PRISM_ISO&luxSurface=kpiWidget&luxPerf=perf&luxMotion=off&debug=1"
  },
  {
    input: {
      luxStyle: "GOLD_NOIR_TERMINAL",
      luxSurface: "drawer",
      luxPerf: "default",
      luxMotion: "hero",
      luxMaterial: "ink/drawer"
    },
    expected: "luxStyle=GOLD_NOIR_TERMINAL&luxSurface=drawer&luxPerf=default&luxMotion=hero&luxMaterial=ink%2Fdrawer"
  }
] as const);
