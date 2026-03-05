export const STYLE_IDS = ["LIQUID_GLASS", "GOLD_NOIR_TERMINAL", "GRAPHITE_PRISM_ISO"] as const;

export type StyleId = (typeof STYLE_IDS)[number];

export const SURFACE_IDS = [
  "controlRoomHud",
  "pitchCard",
  "pitchPanel",
  "kpiWidget",
  "tableDense",
  "drawer",
  "rail",
  "popover"
] as const;

export type SurfaceId = (typeof SURFACE_IDS)[number];

export const SEMANTIC_INTENTS = [
  "deal",
  "cash",
  "evidence",
  "outcome",
  "governance",
  "risk",
  "neutral"
] as const;

export type SemanticIntent = (typeof SEMANTIC_INTENTS)[number];

export const PERF_PROFILES = ["default", "perf"] as const;

export type PerfProfile = (typeof PERF_PROFILES)[number];

export const MOTION_LEVELS = ["micro", "standard", "hero", "off"] as const;

export type MotionLevel = (typeof MOTION_LEVELS)[number];

export const MATERIAL_IDS = [
  "glass/card",
  "glass/inset",
  "glass/drawer",
  "glass/hero",
  "ink/card",
  "ink/drawer",
  "graphite/card",
  "graphite/inset"
] as const;

export type MaterialId = (typeof MATERIAL_IDS)[number];

const STYLE_ID_SET: ReadonlySet<StyleId> = new Set(STYLE_IDS);
const SURFACE_ID_SET: ReadonlySet<SurfaceId> = new Set(SURFACE_IDS);
const INTENT_SET: ReadonlySet<SemanticIntent> = new Set(SEMANTIC_INTENTS);
const PERF_PROFILE_SET: ReadonlySet<PerfProfile> = new Set(PERF_PROFILES);
const MOTION_LEVEL_SET: ReadonlySet<MotionLevel> = new Set(MOTION_LEVELS);
const MATERIAL_ID_SET: ReadonlySet<MaterialId> = new Set(MATERIAL_IDS);

export function isStyleId(value: string): value is StyleId {
  return STYLE_ID_SET.has(value as StyleId);
}

export function isSurfaceId(value: string): value is SurfaceId {
  return SURFACE_ID_SET.has(value as SurfaceId);
}

export function isSemanticIntent(value: string): value is SemanticIntent {
  return INTENT_SET.has(value as SemanticIntent);
}

export function isPerfProfile(value: string): value is PerfProfile {
  return PERF_PROFILE_SET.has(value as PerfProfile);
}

export function isMotionLevel(value: string): value is MotionLevel {
  return MOTION_LEVEL_SET.has(value as MotionLevel);
}

export function isMaterialId(value: string): value is MaterialId {
  return MATERIAL_ID_SET.has(value as MaterialId);
}

export interface ApplyLuxuryStyleInput {
  readonly styleId: StyleId;
  readonly surfaceId: SurfaceId;
  readonly perfProfile?: PerfProfile;
  readonly motionLevel?: MotionLevel;
}

export interface ApplyLuxuryMaterialInput {
  readonly materialId: MaterialId;
  readonly perfProfile?: PerfProfile;
}

export interface AccentUsageSnapshot {
  readonly screenAccents: readonly SemanticIntent[];
  readonly chartAccents: readonly SemanticIntent[];
}