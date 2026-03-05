import type {
  AccentUsageSnapshot,
  ApplyLuxuryStyleInput,
  MotionLevel,
  PerfProfile,
  SemanticIntent
} from "./types.js";
import { applyLuxuryMaterial, type AppliedLuxuryMaterial } from "./applyLuxuryMaterial.js";
import { resolveMaterialIdForSurface } from "./materials/materialEngine.js";
import {
  createBudgetSnapshot,
  evaluateGovernanceBudget,
  governanceWarnings,
  type GovernanceEvaluation
} from "./governancePolicy.js";
import {
  enforceAccentBudget,
  resolveSemanticAccentPlan,
  SEMANTIC_ACCENT_POLICY,
  type SemanticAccentDecision
} from "./semantics/semanticMap.js";
import { getLuxuryTokens } from "./tokens/index.js";

const STYLE_PIPELINE_TRACE = Object.freeze({
  deriveRule: "component-presets-must-be-derived",
  semanticsRule: "accent-map-driven-by-intent",
  motionRule: "single-hero-otherwise-micro",
  fallbackRule: "perf-or-no-blur-uses-safe-final-state",
  governanceRule: "budget-check-after-material-and-accent-resolution"
});

export interface AppliedLuxuryStyle {
  readonly styleId: ApplyLuxuryStyleInput["styleId"];
  readonly surfaceId: ApplyLuxuryStyleInput["surfaceId"];
  readonly materialId: AppliedLuxuryMaterial["materialId"];
  readonly perfProfile: PerfProfile;
  readonly motionLevel: MotionLevel;
  readonly material: AppliedLuxuryMaterial;
  readonly cssVars: Readonly<Record<string, string>>;
  readonly dataAttributes: Readonly<Record<string, string>>;
  readonly surfaceAccents: readonly SemanticAccentDecision[];
  readonly chartAccents: readonly SemanticAccentDecision[];
  readonly governance: GovernanceEvaluation;
  readonly warnings: readonly string[];
}

function normalizePerfProfile(perfProfile?: PerfProfile): PerfProfile {
  return perfProfile === "perf" ? "perf" : "default";
}

function normalizeMotionLevel(motionLevel?: MotionLevel): MotionLevel {
  return motionLevel ?? "micro";
}

function computeMotionDuration(tokensMotionMs: number, motionLevel: MotionLevel, perfProfile: PerfProfile): number {
  if (motionLevel === "off") {
    return 0;
  }

  if (perfProfile === "perf") {
    return Math.max(80, Math.round(tokensMotionMs * 0.8));
  }

  return tokensMotionMs;
}

function withDefaultAccents(accentUsage?: AccentUsageSnapshot): AccentUsageSnapshot {
  if (accentUsage) {
    return accentUsage;
  }

  const fallback: readonly SemanticIntent[] = ["neutral"];
  return {
    screenAccents: fallback,
    chartAccents: fallback
  };
}

export function applyLuxuryStyle(
  input: ApplyLuxuryStyleInput & {
    readonly accentUsage?: AccentUsageSnapshot;
    readonly blurSupported?: boolean;
  }
): AppliedLuxuryStyle {
  const perfProfile = normalizePerfProfile(input.perfProfile);
  const motionLevel = normalizeMotionLevel(input.motionLevel);
  const materialId = resolveMaterialIdForSurface(input.styleId, input.surfaceId);
  const materialInput = {
    materialId,
    perfProfile,
    ...(input.blurSupported !== undefined ? { blurSupported: input.blurSupported } : {})
  };
  const material = applyLuxuryMaterial(materialInput);

  const tokens = getLuxuryTokens(input.styleId);
  const accentUsage = withDefaultAccents(input.accentUsage);
  const screenAssessment = enforceAccentBudget(accentUsage.screenAccents, "screen");
  const chartAssessment = enforceAccentBudget(accentUsage.chartAccents, "chart");

  const surfaceAccents = resolveSemanticAccentPlan(
    input.styleId,
    screenAssessment.selected,
    "screen",
    "surface"
  );

  const chartAccents = resolveSemanticAccentPlan(
    input.styleId,
    chartAssessment.selected,
    "chart",
    "chartStroke"
  );

  const motionDuration =
    motionLevel === "hero"
      ? computeMotionDuration(tokens.motion.heroDurationMs, motionLevel, perfProfile)
      : motionLevel === "standard"
        ? computeMotionDuration(tokens.motion.standardDurationMs, motionLevel, perfProfile)
        : computeMotionDuration(tokens.motion.microDurationMs, motionLevel, perfProfile);

  const warnings: string[] = [];
  if (screenAssessment.dropped.length > 0) {
    warnings.push(`screen-accent-budget-exceeded:${SEMANTIC_ACCENT_POLICY.maxAccentsPerScreen}`);
  }

  if (chartAssessment.dropped.length > 0) {
    warnings.push(`chart-accent-budget-exceeded:${SEMANTIC_ACCENT_POLICY.maxAccentsPerChart}`);
  }

  if (motionLevel === "hero") {
    warnings.push("hero-motion-must-remain-single-per-screen");
  }

  const governance = evaluateGovernanceBudget(
    input.styleId,
    tokens,
    createBudgetSnapshot({
      motionLevel,
      surfaceAccents: surfaceAccents.map((entry) => entry.intent),
      chartAccents: chartAccents.map((entry) => entry.intent),
      glowAlpha: material.runtimeFlags.specularEnabled ? Number(material.cssVars["--lux-specular-opacity"]) : 0,
      glowBlurPx: material.runtimeFlags.blurEnabled
        ? Number((material.cssVars["--lux-blur-radius"] ?? "0px").replace("px", ""))
        : 0,
      glowLayers: material.runtimeFlags.specularEnabled ? 1 : 0,
      goldCoverageRatio: material.styleId === "GOLD_NOIR_TERMINAL" ? tokens.goldUsage.maxCoverageRatio : 0,
      goldAccentCount: material.styleId === "GOLD_NOIR_TERMINAL" ? surfaceAccents.length : 0
    })
  );
  warnings.push(...governanceWarnings(governance));

  return {
    styleId: input.styleId,
    surfaceId: input.surfaceId,
    materialId,
    perfProfile,
    motionLevel,
    material,
    cssVars: {
      ...material.cssVars,
      "--lux-ink": tokens.neutral.ink,
      "--lux-slate": tokens.neutral.slate,
      "--lux-pearl": tokens.neutral.pearl,
      "--lux-text-strong": tokens.neutral.textStrong,
      "--lux-text-soft": tokens.neutral.textSoft,
      "--lux-motion-duration": `${motionDuration}ms`,
      "--lux-motion-level": motionLevel,
      "--lux-motion-hero-limit": String(tokens.motion.heroPerScreen),
      "--lux-reduced-motion-final-state": tokens.motion.reducedMotionFinalState ? "1" : "0",
      "--lux-style-pipeline-trace": [
        STYLE_PIPELINE_TRACE.deriveRule,
        STYLE_PIPELINE_TRACE.semanticsRule,
        STYLE_PIPELINE_TRACE.motionRule,
        STYLE_PIPELINE_TRACE.fallbackRule,
        STYLE_PIPELINE_TRACE.governanceRule
      ].join("|")
    },
    dataAttributes: {
      ...material.dataAttributes,
      "data-lux-surface": input.surfaceId,
      "data-lux-motion": motionLevel,
      "data-lux-motion-reduced": motionLevel === "off" ? "1" : "0"
    },
    surfaceAccents,
    chartAccents,
    governance,
    warnings
  };
}
