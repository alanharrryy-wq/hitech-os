import type { SemanticIntent, StyleId } from "../types.js";

export type ElevationLevel = 0 | 1 | 2 | 3;

export interface NeutralRamp {
  readonly ink: string;
  readonly slate: string;
  readonly pearl: string;
  readonly panel: string;
  readonly panelRaised: string;
  readonly textStrong: string;
  readonly textSoft: string;
}

export interface StrokeRamp {
  readonly subtle: string;
  readonly strong: string;
  readonly widthPx: number;
}

export interface ElevationToken {
  readonly surfaceLift: string;
  readonly shadow: string;
  readonly rimLight: string;
}

export type ElevationRamp = Record<ElevationLevel, ElevationToken>;

export interface SemanticAccent {
  readonly primary: string;
  readonly muted: string;
  readonly glow: string;
  readonly chartGradientStart?: string;
  readonly chartGradientEnd?: string;
}

export type SemanticAccentRamp = Record<SemanticIntent, SemanticAccent>;

export interface GlowBudget {
  readonly maxAlpha: number;
  readonly maxBlurPx: number;
  readonly maxLayersPerSurface: number;
}

export interface GoldUsagePolicy {
  readonly enabled: boolean;
  readonly maxCoverageRatio: number;
  readonly maxAccentsPerSurface: number;
  readonly allowTextFill: boolean;
  readonly notes: readonly string[];
}

export interface TexturePolicy {
  readonly grainMaxOpacity: number;
  readonly gridMaxOpacity: number;
  readonly maxTextureLayers: number;
}

export interface MotionBudget {
  readonly heroPerScreen: 1;
  readonly microDurationMs: number;
  readonly standardDurationMs: number;
  readonly heroDurationMs: number;
  readonly reducedMotionFinalState: true;
}

export interface LuxuryTokenPack {
  readonly styleId: StyleId;
  readonly neutral: NeutralRamp;
  readonly hairline: StrokeRamp;
  readonly innerStroke: StrokeRamp;
  readonly elevation: ElevationRamp;
  readonly semantic: SemanticAccentRamp;
  readonly glowBudget: GlowBudget;
  readonly goldUsage: GoldUsagePolicy;
  readonly texture: TexturePolicy;
  readonly motion: MotionBudget;
}

export interface LuxuryPolicyBudgets {
  readonly glow: GlowBudget;
  readonly gold: GoldUsagePolicy;
  readonly motion: MotionBudget;
}

export const SHARED_MOTION_BUDGET: MotionBudget = Object.freeze({
  heroPerScreen: 1,
  microDurationMs: 120,
  standardDurationMs: 180,
  heroDurationMs: 320,
  reducedMotionFinalState: true
});
