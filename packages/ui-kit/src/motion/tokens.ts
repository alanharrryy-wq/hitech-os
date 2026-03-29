export type MotionTier = "micro" | "base" | "hero";
export type MotionProfile = "quality" | "perf";

export interface MotionTierTokens {
  readonly durationMs: number;
  readonly easing: string;
  readonly maxDistancePx: number;
}

export interface MotionTokens {
  readonly micro: MotionTierTokens;
  readonly base: MotionTierTokens;
  readonly hero: MotionTierTokens;
}

export const MOTION_EASINGS = Object.freeze({
  // Mirrors premium pack baseline from hitech-premium.css.
  premium: "cubic-bezier(0.16, 0.84, 0.24, 1)",
  standard: "cubic-bezier(0.22, 0.61, 0.36, 1)",
  settle: "cubic-bezier(0.2, 0.8, 0.2, 1)",
  sweep: "cubic-bezier(0.2, 0.95, 0.3, 1)"
});

export const MOTION_TOKENS: Readonly<Record<MotionProfile, MotionTokens>> = Object.freeze({
  quality: {
    // Premium packs use 120/220/380ms as the primary rhythm.
    micro: { durationMs: 120, easing: MOTION_EASINGS.premium, maxDistancePx: 2 },
    base: { durationMs: 220, easing: MOTION_EASINGS.premium, maxDistancePx: 8 },
    hero: { durationMs: 380, easing: MOTION_EASINGS.sweep, maxDistancePx: 20 }
  },
  perf: {
    // Perf trims duration and travel while preserving visual hierarchy.
    micro: { durationMs: 90, easing: MOTION_EASINGS.standard, maxDistancePx: 1 },
    base: { durationMs: 160, easing: MOTION_EASINGS.standard, maxDistancePx: 4 },
    hero: { durationMs: 240, easing: MOTION_EASINGS.standard, maxDistancePx: 10 }
  }
});

export const DEFAULT_MOTION_PROFILE: MotionProfile = "quality";

export const MOTION_LIMITS = Object.freeze({
  hoverLiftPx: 2,
  hoverLiftPerfPx: 1,
  enterFadeUpPx: 8,
  enterFadeUpPerfPx: 4,
  heroSweepTravelPercent: 120,
  skeletonShimmerTravelPercent: 160
});

// Deterministic catalog counts used for calibration/audit snapshots.
export const MOTION_CATALOG_COUNTS = Object.freeze({
  microQuality: 1400,
  microPerf: 1400,
  baseQuality: 1400,
  basePerf: 1400,
  heroQuality: 1400
});

export const MOTION_CATALOG_TOTAL_ROWS = Object.values(MOTION_CATALOG_COUNTS).reduce(
  (sum, value) => sum + value,
  0
);

export function resolveMotionTokens(profile: MotionProfile = DEFAULT_MOTION_PROFILE): MotionTokens {
  return MOTION_TOKENS[profile];
}

export function resolveTierTokens(
  tier: MotionTier,
  profile: MotionProfile = DEFAULT_MOTION_PROFILE
): MotionTierTokens {
  return resolveMotionTokens(profile)[tier];
}

export function toMs(durationMs: number): string {
  return `${Math.max(0, Math.round(durationMs))}ms`;
}
