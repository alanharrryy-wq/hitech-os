import type { MotionLevel, SemanticIntent, StyleId } from "./types.js";
import type { LuxuryTokenPack } from "./tokens/types.js";

export type GovernanceCheckStatus = "OK" | "WARN";

export interface GovernanceBudgetSnapshot {
  readonly glowAlpha: number;
  readonly glowBlurPx: number;
  readonly glowLayers: number;
  readonly goldCoverageRatio: number;
  readonly goldAccentCount: number;
  readonly heroMotionCount: number;
  readonly screenAccentCount: number;
  readonly chartAccentCount: number;
}

export interface GovernanceCheck {
  readonly id:
    | "glow-alpha"
    | "glow-blur"
    | "glow-layers"
    | "gold-coverage"
    | "gold-accents"
    | "hero-motion"
    | "screen-accents"
    | "chart-accents";
  readonly status: GovernanceCheckStatus;
  readonly message: string;
}

export interface GovernanceEvaluation {
  readonly styleId: StyleId;
  readonly status: GovernanceCheckStatus;
  readonly checks: readonly GovernanceCheck[];
}

const MAX_SCREEN_ACCENTS = 3;
const MAX_CHART_ACCENTS = 4;
const MAX_HERO_MOTION_PER_SCREEN = 1;

function evaluateBound(
  id: GovernanceCheck["id"],
  value: number,
  max: number,
  label: string
): GovernanceCheck {
  if (value <= max) {
    return {
      id,
      status: "OK",
      message: `${label}=${value} within max=${max}`
    };
  }

  return {
    id,
    status: "WARN",
    message: `${label}=${value} exceeds max=${max}`
  };
}

export function evaluateGovernanceBudget(
  styleId: StyleId,
  tokens: LuxuryTokenPack,
  snapshot: GovernanceBudgetSnapshot
): GovernanceEvaluation {
  const checks: GovernanceCheck[] = [
    evaluateBound("glow-alpha", snapshot.glowAlpha, tokens.glowBudget.maxAlpha, "glowAlpha"),
    evaluateBound("glow-blur", snapshot.glowBlurPx, tokens.glowBudget.maxBlurPx, "glowBlurPx"),
    evaluateBound("glow-layers", snapshot.glowLayers, tokens.glowBudget.maxLayersPerSurface, "glowLayers"),
    evaluateBound("gold-coverage", snapshot.goldCoverageRatio, tokens.goldUsage.maxCoverageRatio, "goldCoverageRatio"),
    evaluateBound("gold-accents", snapshot.goldAccentCount, tokens.goldUsage.maxAccentsPerSurface, "goldAccentCount"),
    evaluateBound("hero-motion", snapshot.heroMotionCount, MAX_HERO_MOTION_PER_SCREEN, "heroMotionCount"),
    evaluateBound("screen-accents", snapshot.screenAccentCount, MAX_SCREEN_ACCENTS, "screenAccentCount"),
    evaluateBound("chart-accents", snapshot.chartAccentCount, MAX_CHART_ACCENTS, "chartAccentCount")
  ];

  return {
    styleId,
    status: checks.some((check) => check.status === "WARN") ? "WARN" : "OK",
    checks
  };
}

export function createBudgetSnapshot(input: {
  readonly motionLevel: MotionLevel;
  readonly surfaceAccents: readonly SemanticIntent[];
  readonly chartAccents: readonly SemanticIntent[];
  readonly glowAlpha: number;
  readonly glowBlurPx: number;
  readonly glowLayers: number;
  readonly goldCoverageRatio: number;
  readonly goldAccentCount: number;
}): GovernanceBudgetSnapshot {
  return {
    glowAlpha: input.glowAlpha,
    glowBlurPx: input.glowBlurPx,
    glowLayers: input.glowLayers,
    goldCoverageRatio: input.goldCoverageRatio,
    goldAccentCount: input.goldAccentCount,
    heroMotionCount: input.motionLevel === "hero" ? 1 : 0,
    screenAccentCount: input.surfaceAccents.length,
    chartAccentCount: input.chartAccents.length
  };
}

export function governanceWarnings(evaluation: GovernanceEvaluation): readonly string[] {
  return evaluation.checks
    .filter((check) => check.status === "WARN")
    .map((check) => `${check.id}:${check.message}`);
}

export function mergeSnapshots(
  primary: GovernanceBudgetSnapshot,
  secondary: GovernanceBudgetSnapshot
): GovernanceBudgetSnapshot {
  return {
    glowAlpha: Math.max(primary.glowAlpha, secondary.glowAlpha),
    glowBlurPx: Math.max(primary.glowBlurPx, secondary.glowBlurPx),
    glowLayers: Math.max(primary.glowLayers, secondary.glowLayers),
    goldCoverageRatio: Math.max(primary.goldCoverageRatio, secondary.goldCoverageRatio),
    goldAccentCount: Math.max(primary.goldAccentCount, secondary.goldAccentCount),
    heroMotionCount: primary.heroMotionCount + secondary.heroMotionCount,
    screenAccentCount: primary.screenAccentCount + secondary.screenAccentCount,
    chartAccentCount: primary.chartAccentCount + secondary.chartAccentCount
  };
}
