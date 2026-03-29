import type { SemanticIntent, StyleId } from "../types.js";
import { getLuxuryTokens } from "../tokens/index.js";

export type SemanticTarget = "surface" | "text" | "chartStroke" | "chartFill";
export type AccentContext = "screen" | "chart";

export interface SemanticAccentDecision {
  readonly styleId: StyleId;
  readonly intent: SemanticIntent;
  readonly target: SemanticTarget;
  readonly color: string;
  readonly muted: string;
  readonly glow: string;
  readonly gradient?: {
    readonly start: string;
    readonly end: string;
    readonly scope: "chart-data-only";
  };
}

export interface AccentBudgetAssessment {
  readonly context: AccentContext;
  readonly maxAllowed: number;
  readonly selected: readonly SemanticIntent[];
  readonly dropped: readonly SemanticIntent[];
}

export const SEMANTIC_ACCENT_POLICY = Object.freeze({
  maxAccentsPerScreen: 3,
  maxAccentsPerChart: 4,
  graphitePrismGradientScope: "chart-data-only" as const,
  deriveDontInvent: true,
  semanticOverDecoration: true
});

function uniqueIntents(intents: readonly SemanticIntent[]): SemanticIntent[] {
  return [...new Set(intents)];
}

export function enforceAccentBudget(
  intents: readonly SemanticIntent[],
  context: AccentContext
): AccentBudgetAssessment {
  const unique = uniqueIntents(intents);
  const maxAllowed = context === "screen" ? SEMANTIC_ACCENT_POLICY.maxAccentsPerScreen : SEMANTIC_ACCENT_POLICY.maxAccentsPerChart;

  return {
    context,
    maxAllowed,
    selected: unique.slice(0, maxAllowed),
    dropped: unique.slice(maxAllowed)
  };
}

export function resolveSemanticAccent(
  styleId: StyleId,
  intent: SemanticIntent,
  target: SemanticTarget
): SemanticAccentDecision {
  const accent = getLuxuryTokens(styleId).semantic[intent];

  if (styleId !== "GRAPHITE_PRISM_ISO") {
    return {
      styleId,
      intent,
      target,
      color: accent.primary,
      muted: accent.muted,
      glow: accent.glow
    };
  }

  const canUseGradient = target === "chartStroke" || target === "chartFill";

  return {
    styleId,
    intent,
    target,
    color: accent.primary,
    muted: accent.muted,
    glow: accent.glow,
    ...(canUseGradient && accent.chartGradientStart && accent.chartGradientEnd
      ? {
          gradient: {
            start: accent.chartGradientStart,
            end: accent.chartGradientEnd,
            scope: SEMANTIC_ACCENT_POLICY.graphitePrismGradientScope
          }
        }
      : {})
  };
}

export function resolveSemanticAccentPlan(
  styleId: StyleId,
  intents: readonly SemanticIntent[],
  context: AccentContext,
  target: SemanticTarget
): ReadonlyArray<SemanticAccentDecision> {
  const constrained = enforceAccentBudget(intents, context);
  return constrained.selected.map((intent) => resolveSemanticAccent(styleId, intent, target));
}
