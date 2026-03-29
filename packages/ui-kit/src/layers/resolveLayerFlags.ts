import {
  ALL_LAYERS,
  applyLayerPreset,
  createAllLayersOff,
  createAllLayersOn,
  createFlagsFromEnabledLayers,
  isLayerId,
  listEnabledLayers,
  mergeLayerFlags,
  sortLayerIds,
  type LayerFlags,
  type LayerId,
  type LayerProfile
} from "./layerIds.js";

export type SearchParamsLike = Record<string, string | string[] | undefined>;

export interface LayerResolveRaw {
  readonly layers?: string;
  readonly layerProfile?: string;
  readonly motion?: string;
  readonly debug?: string;
}

export type LayerBaseSource = "layers" | "profile" | "default";
export type LayerResolutionSource = LayerBaseSource | "mixed";
export type LayerMotionSource = "layers" | "profile" | "default" | "motion";

export interface ParsedLayersQueryValue {
  readonly layerIds: readonly LayerId[];
  readonly unknownTokens: readonly string[];
  readonly motionAliasOn: boolean;
}

export interface ResolvedLayerFlags {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly source: LayerResolutionSource;
  readonly baseSource: LayerBaseSource;
  readonly motionSource: LayerMotionSource;
  readonly unknownTokens: readonly string[];
  readonly raw: LayerResolveRaw;
}

export const LAYER_QUERY_KEY_ORDER = ["layers", "layerProfile", "motion", "debug"] as const;

type LayerResolveRawInput = {
  readonly layers?: string | undefined;
  readonly layerProfile?: string | undefined;
  readonly motion?: string | undefined;
  readonly debug?: string | undefined;
};
type ResolvedLayerInput = {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly baseSource: LayerBaseSource;
  readonly motionSource: LayerMotionSource;
  readonly unknownTokens?: readonly string[];
  readonly raw: LayerResolveRaw;
};

const NON_MOTION_LAYER_IDS = ALL_LAYERS.filter((id) => id !== "motion.enabled");

function buildRaw(raw: LayerResolveRawInput): LayerResolveRaw {
  return {
    ...(raw.layers !== undefined ? { layers: raw.layers } : {}),
    ...(raw.layerProfile !== undefined ? { layerProfile: raw.layerProfile } : {}),
    ...(raw.motion !== undefined ? { motion: raw.motion } : {}),
    ...(raw.debug !== undefined ? { debug: raw.debug } : {})
  };
}

function firstParam(value: string | string[] | undefined): string | undefined {
  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    return value[0];
  }

  return undefined;
}

function normalizeProfile(value: string | undefined): LayerProfile | undefined {
  if (value === "neutral" || value === "fx" || value === "perf") {
    return value;
  }

  return undefined;
}

function normalizeDebug(value: string | undefined): boolean {
  return value === "1";
}

function normalizeLayersValue(value: string | undefined): string | undefined {
  if (!value) {
    return undefined;
  }

  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return undefined;
  }

  return trimmed;
}

function normalizeMotionValue(value: string | undefined): boolean | undefined {
  if (!value) {
    return undefined;
  }

  const normalized = value.trim().toLowerCase();
  if (normalized === "on" || normalized === "1" || normalized === "true") {
    return true;
  }

  if (normalized === "off" || normalized === "0" || normalized === "false") {
    return false;
  }

  return undefined;
}

function encodeMotionParam(enabled: boolean): "on" | "off" {
  return enabled ? "on" : "off";
}

export function deriveLayerResolutionSource(
  baseSource: LayerBaseSource,
  motionSource: LayerMotionSource
): LayerResolutionSource {
  if (baseSource === "layers") {
    return "layers";
  }

  if (motionSource === "motion" || motionSource === "layers") {
    return "mixed";
  }

  if (motionSource !== baseSource) {
    return "mixed";
  }

  return baseSource;
}

function createResolved(input: ResolvedLayerInput): ResolvedLayerFlags {
  return {
    flags: input.flags,
    profile: input.profile,
    debug: input.debug,
    source: deriveLayerResolutionSource(input.baseSource, input.motionSource),
    baseSource: input.baseSource,
    motionSource: input.motionSource,
    unknownTokens: input.unknownTokens ?? [],
    raw: input.raw
  };
}

function shouldPersistMotionParamFromState(input: {
  readonly flags: LayerFlags;
  readonly motionSource: LayerMotionSource;
}): boolean {
  if (input.motionSource === "motion") {
    return true;
  }

  return input.flags["motion.enabled"];
}

function toRawFromResolvedState(input: {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly baseSource: LayerBaseSource;
  readonly motionSource: LayerMotionSource;
}): LayerResolveRaw {
  const includeMotion = shouldPersistMotionParamFromState(input);

  return buildRaw({
    layers: input.baseSource === "layers" ? encodeLayersParam(input.flags) : undefined,
    layerProfile: input.baseSource === "profile" ? input.profile : undefined,
    motion: includeMotion ? encodeMotionParam(input.flags["motion.enabled"]) : undefined,
    debug: input.debug ? "1" : undefined
  });
}

function resolveFromLayers(rawLayers: string): {
  readonly flags: LayerFlags;
  readonly unknownTokens: readonly string[];
  readonly motionAliasOn: boolean;
} {
  if (rawLayers === "none") {
    return {
      flags: createAllLayersOff(),
      unknownTokens: [],
      motionAliasOn: false
    };
  }

  if (rawLayers === "all") {
    return {
      flags: createAllLayersOn(),
      unknownTokens: [],
      motionAliasOn: false
    };
  }

  const parsed = parseLayersQueryValue(rawLayers);
  const base = createFlagsFromEnabledLayers(parsed.layerIds);
  const flags = parsed.motionAliasOn
    ? mergeLayerFlags(base, { "motion.enabled": true })
    : base;

  return {
    flags,
    unknownTokens: parsed.unknownTokens,
    motionAliasOn: parsed.motionAliasOn
  };
}

function resolveFromProfile(profile: LayerProfile): LayerFlags {
  return applyLayerPreset(profile);
}

export function parseLayersQueryValue(rawLayers: string): ParsedLayersQueryValue {
  const tokens = rawLayers
    .split(",")
    .map((value) => value.trim())
    .filter((value) => value.length > 0);

  const layerIds = new Set<LayerId>();
  const unknownTokens = new Set<string>();
  let motionAliasOn = false;

  for (const token of tokens) {
    if (token === "motion.enabled") {
      motionAliasOn = true;
      continue;
    }

    if (isLayerId(token)) {
      layerIds.add(token);
      continue;
    }

    unknownTokens.add(token);
  }

  return {
    layerIds: sortLayerIds([...layerIds]),
    unknownTokens: [...unknownTokens],
    motionAliasOn
  };
}

export function resolveLayerFlags(searchParams: SearchParamsLike): ResolvedLayerFlags {
  const rawLayers = normalizeLayersValue(firstParam(searchParams["layers"]));
  const rawProfile = firstParam(searchParams["layerProfile"]);
  const rawMotion = firstParam(searchParams["motion"]);
  const rawDebug = firstParam(searchParams["debug"]);

  const profile = normalizeProfile(rawProfile) ?? "neutral";
  const debug = normalizeDebug(rawDebug);
  const explicitMotion = normalizeMotionValue(rawMotion);

  let flags = createAllLayersOff();
  let baseSource: LayerBaseSource = "default";
  let motionSource: LayerMotionSource = "default";
  let unknownTokens: readonly string[] = [];
  let motionAliasOn = false;

  if (normalizeProfile(rawProfile)) {
    flags = resolveFromProfile(profile);
    baseSource = "profile";
    motionSource = "profile";
  }

  if (rawLayers) {
    const layerResolution = resolveFromLayers(rawLayers);
    flags = layerResolution.flags;
    baseSource = "layers";
    motionSource = "layers";
    unknownTokens = layerResolution.unknownTokens;
    motionAliasOn = layerResolution.motionAliasOn;
  }

  if (explicitMotion !== undefined) {
    flags = mergeLayerFlags(flags, { "motion.enabled": explicitMotion });
    motionSource = "motion";
  } else if (motionAliasOn) {
    motionSource = "layers";
  }

  return createResolved({
    flags,
    profile,
    debug,
    baseSource,
    motionSource,
    unknownTokens,
    raw: buildRaw({
      layers: rawLayers,
      layerProfile: rawProfile,
      motion: rawMotion,
      debug: rawDebug
    })
  });
}

export function encodeLayersParam(flags: LayerFlags): string {
  const allNonMotionEnabled = NON_MOTION_LAYER_IDS.every((id) => flags[id]);
  if (allNonMotionEnabled) {
    return "all";
  }

  const allNonMotionDisabled = NON_MOTION_LAYER_IDS.every((id) => !flags[id]);
  if (allNonMotionDisabled) {
    return "none";
  }

  return listEnabledLayers(flags)
    .filter((id) => id !== "motion.enabled")
    .join(",");
}

export function canonicalizeLayerQuery(search: URLSearchParams): URLSearchParams {
  const ordered = new URLSearchParams();
  const usedKeys = new Set<string>();

  for (const key of LAYER_QUERY_KEY_ORDER) {
    usedKeys.add(key);
    for (const value of search.getAll(key)) {
      ordered.append(key, value);
    }
  }

  const remainingKeys = [...new Set(search.keys())]
    .filter((key) => !usedKeys.has(key))
    .sort((left, right) => left.localeCompare(right));

  for (const key of remainingKeys) {
    for (const value of search.getAll(key)) {
      ordered.append(key, value);
    }
  }

  return ordered;
}

function applyBaseSourceToQuery(
  next: URLSearchParams,
  resolved: Pick<ResolvedLayerFlags, "flags" | "profile" | "baseSource">
): void {
  if (resolved.baseSource === "layers") {
    next.set("layers", encodeLayersParam(resolved.flags));
  } else if (resolved.baseSource === "profile") {
    next.set("layerProfile", resolved.profile);
  }
}

function applyMotionToQuery(
  next: URLSearchParams,
  resolved: Pick<ResolvedLayerFlags, "flags" | "motionSource">
): void {
  const includeMotion = shouldPersistMotionParamFromState({
    flags: resolved.flags,
    motionSource: resolved.motionSource
  });

  if (!includeMotion) {
    return;
  }

  next.set("motion", encodeMotionParam(resolved.flags["motion.enabled"]));
}

function clearLayerQueryKeys(search: URLSearchParams): void {
  for (const key of LAYER_QUERY_KEY_ORDER) {
    search.delete(key);
  }
}

export function createLayerFlagsQueryFromResolved(
  resolved: ResolvedLayerFlags,
  currentSearch: URLSearchParams
): URLSearchParams {
  const next = new URLSearchParams(currentSearch);
  clearLayerQueryKeys(next);

  applyBaseSourceToQuery(next, resolved);
  applyMotionToQuery(next, resolved);

  if (resolved.debug) {
    next.set("debug", "1");
  }

  return canonicalizeLayerQuery(next);
}

export function createShareableLayerUrl(
  resolved: ResolvedLayerFlags,
  current: {
    readonly origin: string;
    readonly pathname: string;
    readonly search?: string;
  }
): string {
  const baseSearch = new URLSearchParams(current.search ?? "");
  const next = createLayerFlagsQueryFromResolved(resolved, baseSearch);
  const query = next.toString();
  return query.length > 0
    ? `${current.origin}${current.pathname}?${query}`
    : `${current.origin}${current.pathname}`;
}

export function createResolvedFromProfile(
  profile: LayerProfile,
  debug = false
): ResolvedLayerFlags {
  const flags = applyLayerPreset(profile);
  const baseSource: LayerBaseSource = profile === "neutral" ? "default" : "profile";
  const motionSource: LayerMotionSource = baseSource;

  return createResolved({
    flags,
    profile,
    debug,
    baseSource,
    motionSource,
    raw: toRawFromResolvedState({
      flags,
      profile,
      debug,
      baseSource,
      motionSource
    })
  });
}

export function createResolvedFromLayers(
  enabledLayers: readonly LayerId[],
  debug = false
): ResolvedLayerFlags {
  const flags = createFlagsFromEnabledLayers(enabledLayers);
  const baseSource: LayerBaseSource = "layers";
  const motionSource: LayerMotionSource = "layers";

  return createResolved({
    flags,
    profile: "neutral",
    debug,
    baseSource,
    motionSource,
    raw: toRawFromResolvedState({
      flags,
      profile: "neutral",
      debug,
      baseSource,
      motionSource
    })
  });
}

export function overrideResolvedFlags(
  resolved: ResolvedLayerFlags,
  overrides?: Partial<LayerFlags>
): ResolvedLayerFlags {
  if (!overrides) {
    return resolved;
  }

  const flags = mergeLayerFlags(resolved.flags, overrides);
  const motionSource: LayerMotionSource =
    overrides["motion.enabled"] === undefined ? resolved.motionSource : "motion";

  return createResolved({
    ...resolved,
    flags,
    motionSource,
    unknownTokens: [],
    raw: toRawFromResolvedState({
      flags,
      profile: resolved.profile,
      debug: resolved.debug,
      baseSource: resolved.baseSource,
      motionSource
    })
  });
}

export function toLayerFlagPairs(flags: LayerFlags): ReadonlyArray<{ id: LayerId; on: boolean }> {
  return ALL_LAYERS.map((id) => ({ id, on: flags[id] }));
}
