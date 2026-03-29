import { isLayerId, sortLayerIds, type LayerId } from "@hitech/ui-kit";
import {
  SCENE_LAYER_PROFILE_VALUES,
  SCENE_LAYERS_MODE_VALUES,
  SCENE_MOTION_VALUES,
  SCENE_QUERY_PRIORITY_KEYS,
  type SceneLayerProfile,
  type SceneLayersMode,
  type SceneMotionValue
} from "./scene-constants";

export type SceneQueryValue = string | readonly string[];
export type SceneQueryObject = Record<string, SceneQueryValue>;

export interface ParsedLayersExpression {
  readonly mode: SceneLayersMode;
  readonly layerIds: readonly LayerId[];
  readonly unknownLayerTokens: readonly string[];
  readonly motionAliasOn: boolean;
}

const PROFILE_SET = new Set<string>(SCENE_LAYER_PROFILE_VALUES);
const MOTION_SET = new Set<string>(SCENE_MOTION_VALUES);

function appendQueryValue(search: URLSearchParams, key: string, value: SceneQueryValue): void {
  if (typeof value === "string") {
    search.append(key, value);
    return;
  }

  for (const entry of value) {
    search.append(key, entry);
  }
}

export function parseSceneQueryToObject(rawQuery: string): SceneQueryObject {
  const query = rawQuery.startsWith("?") ? rawQuery.slice(1) : rawQuery;
  const search = new URLSearchParams(query);
  const result: SceneQueryObject = {};

  for (const key of [...new Set(search.keys())]) {
    const values = search.getAll(key);
    if (values.length === 1) {
      result[key] = values[0] ?? "";
      continue;
    }

    result[key] = values;
  }

  return result;
}

export function sceneQueryObjectToSearchParams(query: SceneQueryObject): URLSearchParams {
  const search = new URLSearchParams();
  for (const key of Object.keys(query)) {
    const value = query[key];
    if (value === undefined) {
      continue;
    }

    appendQueryValue(search, key, value);
  }
  return search;
}

export function canonicalizeSceneQuery(search: URLSearchParams): URLSearchParams {
  const canonical = new URLSearchParams();
  const consumed = new Set<string>();

  for (const key of SCENE_QUERY_PRIORITY_KEYS) {
    consumed.add(key);
    for (const value of search.getAll(key)) {
      canonical.append(key, value);
    }
  }

  const remaining = [...new Set(search.keys())]
    .filter((key) => !consumed.has(key))
    .sort((left, right) => left.localeCompare(right));

  for (const key of remaining) {
    for (const value of search.getAll(key)) {
      canonical.append(key, value);
    }
  }

  return canonical;
}

function stringifyCanonicalSceneQuery(search: URLSearchParams): string {
  return search.toString().replaceAll("%2C", ",");
}

export function serializeSceneQuery(query: SceneQueryObject): string {
  const canonical = canonicalizeSceneQuery(sceneQueryObjectToSearchParams(query));
  return stringifyCanonicalSceneQuery(canonical);
}

export function normalizeLayersList(ids: readonly LayerId[]): LayerId[] {
  return sortLayerIds(Array.from(new Set(ids)));
}

export function parseLayersExpression(rawLayers: string): ParsedLayersExpression {
  const trimmed = rawLayers.trim();
  if (trimmed === "none") {
    return {
      mode: "none",
      layerIds: [],
      unknownLayerTokens: [],
      motionAliasOn: false
    };
  }

  if (trimmed === "all") {
    return {
      mode: "all",
      layerIds: [],
      unknownLayerTokens: [],
      motionAliasOn: false
    };
  }

  const tokens = trimmed
    .split(",")
    .map((token) => token.trim())
    .filter((token) => token.length > 0);

  const layerIds = new Set<LayerId>();
  const unknownLayerTokens = new Set<string>();
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

    unknownLayerTokens.add(token);
  }

  return {
    mode: "list",
    layerIds: normalizeLayersList([...layerIds]),
    unknownLayerTokens: [...unknownLayerTokens],
    motionAliasOn
  };
}

export function parseSceneLayerProfile(value: string | undefined): SceneLayerProfile {
  if (!value) {
    return "neutral";
  }

  const normalized = value.trim();
  return PROFILE_SET.has(normalized) ? (normalized as SceneLayerProfile) : "neutral";
}

export function parseSceneMotion(value: string | undefined): SceneMotionValue {
  if (!value) {
    return "off";
  }

  const normalized = value.trim().toLowerCase();
  if (normalized === "1" || normalized === "true") {
    return "on";
  }

  if (normalized === "0" || normalized === "false") {
    return "off";
  }

  return MOTION_SET.has(normalized) ? (normalized as SceneMotionValue) : "off";
}

export function parseSceneLayersMode(value: string | undefined): SceneLayersMode {
  if (!value) {
    return "none";
  }

  const normalized = value.trim();
  return SCENE_LAYERS_MODE_VALUES.includes(normalized as SceneLayersMode)
    ? (normalized as SceneLayersMode)
    : "none";
}

export function buildLayersQueryValue(mode: SceneLayersMode, layerIds: readonly LayerId[]): string {
  if (mode === "none") {
    return "none";
  }

  if (mode === "all") {
    return "all";
  }

  return normalizeLayersList(layerIds).join(",");
}

export function detectUnknownLayers(layerIds: readonly string[]): string[] {
  return [...new Set(layerIds.filter((id) => !isLayerId(id) && id !== "motion.enabled"))].sort();
}

export function parseSceneQueryFromUrl(rawQuery: string): {
  readonly queryObject: SceneQueryObject;
  readonly canonicalQuery: string;
} {
  const queryObject = parseSceneQueryToObject(rawQuery);
  return {
    queryObject,
    canonicalQuery: serializeSceneQuery(queryObject)
  };
}
