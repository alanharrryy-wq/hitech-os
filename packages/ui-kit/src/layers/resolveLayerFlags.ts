import {
  CANON_LAYER_IDS,
  DEFAULT_LAYER_PROFILE,
  EXPENSIVE_LAYER_IDS,
  PROFILE_LAYER_FLAGS,
  buildDataAttrStateForFlags,
  cloneLayerFlags,
  createAllLayersOff,
  createAllLayersOn,
  createLayerFlags,
  getDisabledLayerIds,
  getEnabledLayerIds,
  isLayerId,
  isLayerProfileId,
  normalizeLayerToken,
  stableSortLayerIds,
  type LayerDataAttrState,
  type LayerFlags,
  type LayerId,
  type LayerProfileId,
  type MutableLayerFlags,
} from "./layerIds.js";

const DEBUG_TRUE_VALUES = new Set(["1", "true", "yes", "on"]);

export type LayerResolutionSource = "layers" | "layerProfile" | "default";

export type LayersDirectiveMode = "none" | "all" | "allowlist";

export interface ResolveLayerFlagsInput {
  readonly search?: string;
  readonly layers?: string | null;
  readonly layerProfile?: string | null;
  readonly debug?: string | number | boolean | null;
  readonly isDevelopment?: boolean;
}

export interface LayerQueryState {
  readonly search: string;
  readonly layersRaw: string | null;
  readonly layerProfileRaw: string | null;
  readonly debugRaw: string | null;
}

export interface ParsedLayersDirective {
  readonly mode: LayersDirectiveMode;
  readonly knownLayerIds: readonly LayerId[];
  readonly unknownLayerIds: readonly string[];
  readonly normalizedTokens: readonly string[];
}

export interface LayerBudgetState {
  readonly motionEnabled: boolean;
  readonly blurEnabled: boolean;
  readonly expensiveEnabledLayerIds: readonly LayerId[];
}

export interface ResolvedLayerFlags {
  readonly flags: LayerFlags;
  readonly source: LayerResolutionSource;
  readonly profile: LayerProfileId;
  readonly layersDirective: LayersDirectiveMode | null;
  readonly knownRequestedLayerIds: readonly LayerId[];
  readonly unknownLayerIds: readonly string[];
  readonly enabledLayerIds: readonly LayerId[];
  readonly disabledLayerIds: readonly LayerId[];
  readonly debugRequested: boolean;
  readonly debugPanelEnabled: boolean;
  readonly query: LayerQueryState;
  readonly budget: LayerBudgetState;
  readonly dataAttrs: LayerDataAttrState;
}

function runtimeIsDevelopment(): boolean {
  if (typeof process === "undefined") {
    return true;
  }
  return process.env.NODE_ENV !== "production";
}

function toNullableString(value: unknown): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  return String(value);
}

function normalizeSearch(value: string | undefined): string {
  const raw = (value ?? "").trim();
  if (!raw) {
    return "";
  }

  if (raw.includes("://")) {
    try {
      return new URL(raw).search;
    } catch {
      return "";
    }
  }

  if (raw.startsWith("?")) {
    return raw;
  }

  const qIndex = raw.indexOf("?");
  if (qIndex >= 0) {
    return raw.slice(qIndex);
  }

  return `?${raw}`;
}

function getLastQueryValue(searchParams: URLSearchParams, key: string): string | null {
  const values = searchParams.getAll(key);
  if (!values.length) {
    return null;
  }
  return values[values.length - 1] ?? null;
}

export function readLayerQuery(input: ResolveLayerFlagsInput): LayerQueryState {
  const search = normalizeSearch(input.search);
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);

  const layersRaw = input.layers === undefined ? getLastQueryValue(params, "layers") : toNullableString(input.layers);
  const layerProfileRaw =
    input.layerProfile === undefined ? getLastQueryValue(params, "layerProfile") : toNullableString(input.layerProfile);
  const debugRaw = input.debug === undefined ? getLastQueryValue(params, "debug") : toNullableString(input.debug);

  return {
    search,
    layersRaw,
    layerProfileRaw,
    debugRaw,
  };
}

export function parseLayerProfile(value: string | null): LayerProfileId | null {
  if (value === null) {
    return null;
  }
  const normalized = normalizeLayerToken(value);
  if (!normalized) {
    return null;
  }
  if (!isLayerProfileId(normalized)) {
    return null;
  }
  return normalized;
}

export function parseDebugRequest(value: string | null): boolean {
  if (value === null) {
    return false;
  }
  return DEBUG_TRUE_VALUES.has(value.trim().toLowerCase());
}

export function parseLayersDirective(value: string | null): ParsedLayersDirective | null {
  if (value === null) {
    return null;
  }

  const normalizedRaw = normalizeLayerToken(value);
  if (normalizedRaw === "none") {
    return {
      mode: "none",
      knownLayerIds: [],
      unknownLayerIds: [],
      normalizedTokens: ["none"],
    };
  }

  if (normalizedRaw === "all") {
    return {
      mode: "all",
      knownLayerIds: [...CANON_LAYER_IDS],
      unknownLayerIds: [],
      normalizedTokens: ["all"],
    };
  }

  const tokens = value
    .split(",")
    .map((token) => normalizeLayerToken(token))
    .filter((token) => token.length > 0);

  const known = new Set<LayerId>();
  const unknown = new Set<string>();

  for (const token of tokens) {
    if (isLayerId(token)) {
      known.add(token);
    } else {
      unknown.add(token);
    }
  }

  const knownLayerIds = stableSortLayerIds([...known]);
  const unknownLayerIds = [...unknown];

  return {
    mode: "allowlist",
    knownLayerIds,
    unknownLayerIds,
    normalizedTokens: tokens,
  };
}

function resolveFlagsFromLayersDirective(directive: ParsedLayersDirective): MutableLayerFlags {
  if (directive.mode === "none") {
    return createAllLayersOff();
  }

  if (directive.mode === "all") {
    return createAllLayersOn();
  }

  return createLayerFlags(directive.knownLayerIds);
}

function resolveFlagsFromProfile(profile: LayerProfileId): MutableLayerFlags {
  return cloneLayerFlags(PROFILE_LAYER_FLAGS[profile]);
}

function buildBudgetState(flags: LayerFlags): LayerBudgetState {
  const expensiveEnabledLayerIds = EXPENSIVE_LAYER_IDS.filter((id) => flags[id]);

  return {
    motionEnabled: flags["motion.enabled"],
    blurEnabled: flags["card.blur"],
    expensiveEnabledLayerIds,
  };
}

export function resolveLayerFlags(input: ResolveLayerFlagsInput = {}): ResolvedLayerFlags {
  const query = readLayerQuery(input);
  const isDevelopment = input.isDevelopment ?? runtimeIsDevelopment();
  const debugRequested = parseDebugRequest(query.debugRaw);

  const parsedLayers = parseLayersDirective(query.layersRaw);
  const parsedProfile = parseLayerProfile(query.layerProfileRaw);

  let source: LayerResolutionSource = "default";
  let profile: LayerProfileId = DEFAULT_LAYER_PROFILE;
  let layersDirective: LayersDirectiveMode | null = null;
  let knownRequestedLayerIds: readonly LayerId[] = [];
  let unknownLayerIds: readonly string[] = [];

  let flags: MutableLayerFlags;

  if (parsedLayers !== null) {
    source = "layers";
    layersDirective = parsedLayers.mode;
    knownRequestedLayerIds = parsedLayers.knownLayerIds;
    unknownLayerIds = parsedLayers.unknownLayerIds;
    flags = resolveFlagsFromLayersDirective(parsedLayers);
  } else if (parsedProfile !== null) {
    source = "layerProfile";
    profile = parsedProfile;
    flags = resolveFlagsFromProfile(profile);
  } else {
    source = "default";
    profile = DEFAULT_LAYER_PROFILE;
    flags = resolveFlagsFromProfile(profile);
  }

  const enabledLayerIds = getEnabledLayerIds(flags);
  const disabledLayerIds = getDisabledLayerIds(flags);
  const budget = buildBudgetState(flags);

  return {
    flags,
    source,
    profile,
    layersDirective,
    knownRequestedLayerIds,
    unknownLayerIds,
    enabledLayerIds,
    disabledLayerIds,
    debugRequested,
    debugPanelEnabled: isDevelopment && debugRequested,
    query,
    budget,
    dataAttrs: buildDataAttrStateForFlags(flags),
  };
}

export function createStableResolvedSnapshot(resolved: ResolvedLayerFlags): string {
  const payload = {
    source: resolved.source,
    profile: resolved.profile,
    layersDirective: resolved.layersDirective,
    knownRequestedLayerIds: [...resolved.knownRequestedLayerIds],
    unknownLayerIds: [...resolved.unknownLayerIds],
    enabledLayerIds: [...resolved.enabledLayerIds],
    disabledLayerIds: [...resolved.disabledLayerIds],
    debugRequested: resolved.debugRequested,
    debugPanelEnabled: resolved.debugPanelEnabled,
    query: {
      search: resolved.query.search,
      layersRaw: resolved.query.layersRaw,
      layerProfileRaw: resolved.query.layerProfileRaw,
      debugRaw: resolved.query.debugRaw,
    },
    budget: {
      motionEnabled: resolved.budget.motionEnabled,
      blurEnabled: resolved.budget.blurEnabled,
      expensiveEnabledLayerIds: [...resolved.budget.expensiveEnabledLayerIds],
    },
    flags: Object.fromEntries(CANON_LAYER_IDS.map((id) => [id, Boolean(resolved.flags[id])])) as Record<string, boolean>,
  };

  return JSON.stringify(payload);
}

export function resolveLayerFlagsFromSearch(search: string, isDevelopment = true): ResolvedLayerFlags {
  return resolveLayerFlags({ search, isDevelopment });
}

export function normalizeLayersQueryHint(resolved: ResolvedLayerFlags): string {
  if (resolved.layersDirective === "none") {
    return "?layers=none";
  }
  if (resolved.layersDirective === "all") {
    return "?layers=all";
  }
  if (resolved.layersDirective === "allowlist") {
    return `?layers=${resolved.knownRequestedLayerIds.join(",")}`;
  }
  return `?layerProfile=${resolved.profile}`;
}

export const __internal = {
  getLastQueryValue,
  normalizeSearch,
};
