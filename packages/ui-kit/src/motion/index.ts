export {
  DEFAULT_MOTION_PROFILE,
  MOTION_CATALOG_COUNTS,
  MOTION_CATALOG_TOTAL_ROWS,
  MOTION_EASINGS,
  MOTION_LIMITS,
  MOTION_TOKENS,
  resolveMotionTokens,
  resolveTierTokens,
  toMs
} from "./tokens.js";
export type { MotionProfile, MotionTier, MotionTierTokens, MotionTokens } from "./tokens.js";

export {
  REDUCED_MOTION_QUERY,
  readSystemReducedMotion,
  resolveMotionDataAttrs,
  resolveMotionGate
} from "./reducedMotion.js";
export type { MotionRuntimeGate, ReducedMotionInput } from "./reducedMotion.js";

export {
  enterFadeUp,
  heroSweep,
  hoverLift,
  pressedInset,
  sheenMicro,
  skeletonShimmer
} from "./primitives.js";
export type { MotionPrimitive, MotionPrimitiveOptions } from "./primitives.js";

export { applyMotion } from "./applyMotion.js";
export type { AppliedMotion, ApplyMotionOptions } from "./applyMotion.js";
