import {
  ALL_LAYERS,
  PROFILE_PRESETS,
  applyLayerPreset,
  areAllLayersDisabled,
  areAllLayersEnabled,
  createAllLayersOff,
  createAllLayersOn,
  createFlagsFromEnabledLayers,
  listEnabledLayers,
  mergeLayerFlags,
  parseLayerList,
  type LayerFlags,
  type LayerId,
  type LayerProfile
} from "./layerIds.js";

export type SearchParamsLike = Record<string, string | string[] | undefined>;

export interface LayerResolveRaw {
  readonly layers?: string;
  readonly layerProfile?: string;
  readonly debug?: string;
}

export interface ResolvedLayerFlags {
  readonly flags: LayerFlags;
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly source: "layers" | "profile" | "default";
  readonly raw: LayerResolveRaw;
}

function buildRaw(raw: {
  layers?: string | undefined;
  layerProfile?: string | undefined;
  debug?: string | undefined;
}): LayerResolveRaw {
  return {
    ...(raw.layers !== undefined ? { layers: raw.layers } : {}),
    ...(raw.layerProfile !== undefined ? { layerProfile: raw.layerProfile } : {}),
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

function resolveFromLayers(rawLayers: string): LayerFlags {
  if (rawLayers === "none") {
    return createAllLayersOff();
  }

  if (rawLayers === "all") {
    return createAllLayersOn();
  }

  const allowlist = parseLayerList(rawLayers);
  return createFlagsFromEnabledLayers(allowlist);
}

function resolveFromProfile(profile: LayerProfile): LayerFlags {
  const preset = PROFILE_PRESETS[profile];
  return createFlagsFromEnabledLayers(preset);
}

export function resolveLayerFlags(searchParams: SearchParamsLike): ResolvedLayerFlags {
  const rawLayers = normalizeLayersValue(firstParam(searchParams["layers"]));
  const rawProfile = firstParam(searchParams["layerProfile"]);
  const rawDebug = firstParam(searchParams["debug"]);

  const profile = normalizeProfile(rawProfile) ?? "neutral";
  const debug = normalizeDebug(rawDebug);

  if (rawLayers) {
    return {
      flags: resolveFromLayers(rawLayers),
      profile,
      debug,
      source: "layers",
      raw: buildRaw({
        layers: rawLayers,
        layerProfile: rawProfile,
        debug: rawDebug
      })
    };
  }

  if (normalizeProfile(rawProfile)) {
    return {
      flags: resolveFromProfile(profile),
      profile,
      debug,
      source: "profile",
      raw: buildRaw({
        layers: rawLayers,
        layerProfile: rawProfile,
        debug: rawDebug
      })
    };
  }

  return {
    flags: createAllLayersOff(),
    profile: "neutral",
    debug,
    source: "default",
    raw: buildRaw({
      layers: rawLayers,
      layerProfile: rawProfile,
      debug: rawDebug
    })
  };
}

export function encodeLayersParam(flags: LayerFlags): string {
  if (areAllLayersEnabled(flags)) {
    return "all";
  }

  if (areAllLayersDisabled(flags)) {
    return "none";
  }

  return listEnabledLayers(flags).join(",");
}

export function createLayerFlagsQueryFromResolved(
  resolved: ResolvedLayerFlags,
  currentSearch: URLSearchParams
): URLSearchParams {
  const next = new URLSearchParams(currentSearch);

  if (resolved.source === "layers") {
    next.set("layers", encodeLayersParam(resolved.flags));
    next.delete("layerProfile");
  }

  if (resolved.source === "profile") {
    next.delete("layers");
    next.set("layerProfile", resolved.profile);
  }

  if (resolved.source === "default") {
    next.delete("layers");
    next.delete("layerProfile");
  }

  if (resolved.debug) {
    next.set("debug", "1");
  } else {
    next.delete("debug");
  }

  return next;
}

export function createResolvedFromProfile(
  profile: LayerProfile,
  debug = false
): ResolvedLayerFlags {
  return {
    flags: applyLayerPreset(profile),
    profile,
    debug,
    source: profile === "neutral" ? "default" : "profile",
    raw: buildRaw({
      layerProfile: profile,
      debug: debug ? "1" : undefined
    })
  };
}

export function createResolvedFromLayers(
  enabledLayers: readonly LayerId[],
  debug = false
): ResolvedLayerFlags {
  const flags = createFlagsFromEnabledLayers(enabledLayers);
  return {
    flags,
    profile: "neutral",
    debug,
    source: "layers",
    raw: buildRaw({
      layers: encodeLayersParam(flags),
      debug: debug ? "1" : undefined
    })
  };
}

export function overrideResolvedFlags(
  resolved: ResolvedLayerFlags,
  overrides?: Partial<LayerFlags>
): ResolvedLayerFlags {
  if (!overrides) {
    return resolved;
  }

  return {
    ...resolved,
    flags: mergeLayerFlags(resolved.flags, overrides),
    source: "layers"
  };
}

export function toLayerFlagPairs(flags: LayerFlags): ReadonlyArray<{ id: LayerId; on: boolean }> {
  return ALL_LAYERS.map((id) => ({ id, on: flags[id] }));
}

export function shouldRenderLayerDebugPanel(
  resolved: Pick<ResolvedLayerFlags, "debug">,
  environment = process.env["NODE_ENV"]
): boolean {
  return environment !== "production" && resolved.debug;
}
