export type {
  AccentUsageSnapshot,
  ApplyLuxuryMaterialInput,
  ApplyLuxuryStyleInput,
  MaterialId,
  MotionLevel,
  PerfProfile,
  SemanticIntent,
  StyleId,
  SurfaceId
} from "./types.js";
export {
  MATERIAL_IDS,
  MOTION_LEVELS,
  PERF_PROFILES,
  SEMANTIC_INTENTS,
  STYLE_IDS,
  SURFACE_IDS,
  isMaterialId,
  isMotionLevel,
  isPerfProfile,
  isSemanticIntent,
  isStyleId,
  isSurfaceId
} from "./types.js";

export { applyLuxuryMaterial } from "./applyLuxuryMaterial.js";
export type { AppliedLuxuryMaterial } from "./applyLuxuryMaterial.js";

export { applyLuxuryStyle } from "./applyLuxuryStyle.js";
export type { AppliedLuxuryStyle } from "./applyLuxuryStyle.js";

export {
  buildExplicitActionQuery,
  normalizeLuxuryQuery,
  parseLuxuryQuery,
  toCanonicalLuxuryQuery,
  type LuxuryQueryState,
  type QueryNormalizationMode
} from "./queryNormalization.js";

export {
  createBudgetSnapshot,
  evaluateGovernanceBudget,
  governanceWarnings,
  mergeSnapshots,
  type GovernanceBudgetSnapshot,
  type GovernanceCheck,
  type GovernanceCheckStatus,
  type GovernanceEvaluation
} from "./governancePolicy.js";

export { LUXURY_TOKEN_PACKS, getLuxuryTokens } from "./tokens/index.js";

export {
  LUXURY_MATERIAL_REGISTRY,
  getLuxuryMaterialRecipe,
  type LuxuryMaterialRecipe
} from "./materials/materialRegistry.js";

export {
  getStyleMaterialStack,
  materialRuntimeToCssVars,
  resolveMaterialIdForSurface,
  resolveMaterialRuntime,
  supportsBackdropBlur,
  type MaterialRuntimeFlags,
  type ResolvedMaterialRuntime
} from "./materials/materialEngine.js";

export {
  SEMANTIC_ACCENT_POLICY,
  enforceAccentBudget,
  resolveSemanticAccent,
  resolveSemanticAccentPlan,
  type AccentBudgetAssessment,
  type SemanticAccentDecision,
  type SemanticTarget
} from "./semantics/semanticMap.js";
