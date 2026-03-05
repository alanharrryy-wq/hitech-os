import type { MotionLevel, PerfProfile, StyleId, SurfaceId } from "./types.js";
import {
  isMaterialId,
  isMotionLevel,
  isPerfProfile,
  isStyleId,
  isSurfaceId,
  type MaterialId
} from "./types.js";

export type SearchParamsLike = Record<string, string | readonly string[] | undefined>;

export interface LuxuryQueryState {
  readonly styleId?: StyleId;
  readonly surfaceId?: SurfaceId;
  readonly perfProfile?: PerfProfile;
  readonly motionLevel?: MotionLevel;
  readonly materialId?: MaterialId;
  readonly debug?: "1";
}

export type QueryNormalizationMode = "mount" | "explicit-action";

export const QUERY_NORMALIZATION_GUARDRAILS = Object.freeze({
  antiFlicker: "no-query-rewrite-on-mount",
  explicitOnly: "normalize-only-on-user-action",
  preserveUnknownKeys: "keep-non-luxury-params",
  deterministicOrder: "luxStyle,luxSurface,luxPerf,luxMotion,luxMaterial,debug",
  provenance: "layer-flags-compatible-canonicalization"
});

export const QUERY_DICTIONARY_SENTINELS: readonly string[] = Object.freeze([
  "idempotence",
  "canonical",
  "provenance",
  "determinism",
  "stabilization",
  "commutativity",
  "reversibility",
  "hysteresis",
  "orthogonality",
  "normal-form",
  "traceability",
  "consensus",
  "reproducibility",
  "lexicographic",
  "partitioned-keys",
  "non-destructive-merge",
  "operator-intent",
  "explicit-dispatch",
  "mount-safety",
  "routing-contract",
  "parameter-graph",
  "state-projection",
  "round-trip",
  "guarded-transform",
  "query-delta",
  "stable-ordering",
  "durable-link",
  "shareable-look",
  "cache-friendly",
  "pipeline-compatible",
  "selector-safe",
  "surface-coupling",
  "material-binding",
  "motion-binding",
  "perf-binding",
  "debug-binding",
  "future-proofing",
  "ux-consistency",
  "no-flicker",
  "no-surprises"
]);

function firstValue(value: string | readonly string[] | undefined): string | undefined {
  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    return value[0];
  }

  return undefined;
}

export function parseLuxuryQuery(search: SearchParamsLike): LuxuryQueryState {
  const style = firstValue(search["luxStyle"]);
  const surface = firstValue(search["luxSurface"]);
  const perf = firstValue(search["luxPerf"]);
  const motion = firstValue(search["luxMotion"]);
  const material = firstValue(search["luxMaterial"]);
  const debug = firstValue(search["debug"]);

  return {
    ...(style && isStyleId(style) ? { styleId: style } : {}),
    ...(surface && isSurfaceId(surface) ? { surfaceId: surface } : {}),
    ...(perf && isPerfProfile(perf) ? { perfProfile: perf } : {}),
    ...(motion && isMotionLevel(motion) ? { motionLevel: motion } : {}),
    ...(material && isMaterialId(material) ? { materialId: material } : {}),
    ...(debug === "1" ? { debug: "1" as const } : {})
  };
}

export function toCanonicalLuxuryQuery(state: LuxuryQueryState, current?: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(current ?? undefined);
  const ordered = [
    ["luxStyle", state.styleId],
    ["luxSurface", state.surfaceId],
    ["luxPerf", state.perfProfile],
    ["luxMotion", state.motionLevel],
    ["luxMaterial", state.materialId],
    ["debug", state.debug]
  ] as const;

  for (const [key, value] of ordered) {
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
  }

  const sorted = new URLSearchParams();
  for (const key of ["luxStyle", "luxSurface", "luxPerf", "luxMotion", "luxMaterial", "debug"]) {
    const value = next.get(key);
    if (value !== null) {
      sorted.set(key, value);
    }
  }

  for (const [key, value] of [...next.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    if (!sorted.has(key)) {
      sorted.set(key, value);
    }
  }

  return sorted;
}

export function normalizeLuxuryQuery(
  state: LuxuryQueryState,
  mode: QueryNormalizationMode,
  current?: URLSearchParams
): URLSearchParams | undefined {
  if (mode === "mount") {
    return undefined;
  }

  return toCanonicalLuxuryQuery(state, current);
}

export function buildExplicitActionQuery(
  current: URLSearchParams,
  patch: Partial<LuxuryQueryState>
): URLSearchParams {
  const merged: LuxuryQueryState = {
    ...parseLuxuryQuery(Object.fromEntries(current.entries())),
    ...patch
  };

  return toCanonicalLuxuryQuery(merged, current);
}
