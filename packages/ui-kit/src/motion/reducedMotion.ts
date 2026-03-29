import {
  DEFAULT_MOTION_PROFILE,
  resolveMotionTokens,
  type MotionProfile,
  type MotionTokens
} from "./tokens.js";

export const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

export interface ReducedMotionInput {
  readonly perfProfile?: MotionProfile;
  readonly motionEnabled?: boolean;
  readonly reducedMotionOverride?: boolean;
  readonly win?: Pick<Window, "matchMedia">;
}

export interface MotionRuntimeGate {
  readonly reducedMotion: boolean;
  readonly profile: MotionProfile;
  readonly motionEnabled: boolean;
  readonly allowAnimation: boolean;
  readonly allowHero: boolean;
  readonly allowShimmer: boolean;
  readonly blurScale: number;
  readonly tokens: MotionTokens;
}

export function readSystemReducedMotion(win?: Pick<Window, "matchMedia">): boolean {
  const target = win ?? (typeof window !== "undefined" ? window : undefined);

  if (!target || typeof target.matchMedia !== "function") {
    return false;
  }

  return target.matchMedia(REDUCED_MOTION_QUERY).matches;
}

export function resolveMotionGate(input: ReducedMotionInput = {}): MotionRuntimeGate {
  const profile = input.perfProfile ?? DEFAULT_MOTION_PROFILE;
  const reducedMotion = input.reducedMotionOverride ?? readSystemReducedMotion(input.win);
  const motionEnabled = input.motionEnabled ?? true;
  const allowAnimation = motionEnabled && !reducedMotion;
  const allowHero = allowAnimation && profile !== "perf";
  const allowShimmer = allowAnimation && profile !== "perf";

  return {
    reducedMotion,
    profile,
    motionEnabled,
    allowAnimation,
    allowHero,
    allowShimmer,
    blurScale: reducedMotion ? 0 : profile === "perf" ? 0.45 : 1,
    tokens: resolveMotionTokens(profile)
  };
}

export function resolveMotionDataAttrs(gate: MotionRuntimeGate): Record<string, string> {
  return {
    "data-ui-motion": gate.reducedMotion ? "reduced" : "enabled",
    "data-ui-motion-enabled": gate.motionEnabled ? "on" : "off",
    "data-ui-perf-profile": gate.profile
  };
}
