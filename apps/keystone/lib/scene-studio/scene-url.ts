import { resolveLayerFlags, sortLayerIds, type LayerId, type LayerProfile, type ResolvedLayerFlags } from "@hitech/ui-kit";
import {
  SCENE_QUERY_PRIORITY_KEYS,
  type SceneLayerProfile,
  type SceneLayersMode,
  type SceneMotionValue
} from "./scene-constants";
import {
  buildLayersQueryValue,
  canonicalizeSceneQuery,
  parseLayersExpression,
  parseSceneMotion,
  parseSceneLayerProfile,
  parseSceneQueryToObject,
  sceneQueryObjectToSearchParams,
  serializeSceneQuery,
  type SceneQueryObject
} from "./scene-query";

export interface SceneUrlState {
  readonly route: string;
  readonly query: string;
  readonly layerProfile: SceneLayerProfile;
  readonly layersMode: SceneLayersMode;
  readonly layerIds: readonly LayerId[];
  readonly motion: SceneMotionValue;
  readonly debug: boolean;
  readonly unknownLayerTokens: readonly string[];
}

export interface BuildSceneUrlInput {
  readonly route: string;
  readonly query?: string | SceneQueryObject;
  readonly layerProfile: SceneLayerProfile;
  readonly layersMode: SceneLayersMode;
  readonly layerIds?: readonly LayerId[];
  readonly motion: SceneMotionValue;
  readonly debug?: boolean;
}

function normalizeRoute(route: string): string {
  if (route.startsWith("/")) {
    return route;
  }

  return `/${route}`;
}

function resolveBaseQuery(query?: string | SceneQueryObject): URLSearchParams {
  if (!query) {
    return new URLSearchParams();
  }

  if (typeof query === "string") {
    return new URLSearchParams(query.startsWith("?") ? query.slice(1) : query);
  }

  return sceneQueryObjectToSearchParams(query);
}

function withSceneControlParams(
  params: URLSearchParams,
  input: Pick<BuildSceneUrlInput, "layerProfile" | "layersMode" | "layerIds" | "motion" | "debug">
): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const key of SCENE_QUERY_PRIORITY_KEYS) {
    next.delete(key);
  }

  next.set("layerProfile", input.layerProfile);
  next.set("layers", buildLayersQueryValue(input.layersMode, input.layerIds ?? []));
  next.set("motion", input.motion);

  if (input.debug) {
    next.set("debug", "1");
  }

  return canonicalizeSceneQuery(next);
}

export function buildCanonicalSceneUrl(input: BuildSceneUrlInput): string {
  const baseQuery = resolveBaseQuery(input.query);
  const next = withSceneControlParams(baseQuery, input);
  const query = next.toString();
  const route = normalizeRoute(input.route);

  return query.length > 0 ? `${route}?${query}` : route;
}

export function buildCanonicalSceneQuery(input: BuildSceneUrlInput): string {
  const baseQuery = resolveBaseQuery(input.query);
  const next = withSceneControlParams(baseQuery, input);
  return next.toString().replaceAll("%2C", ",");
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

export function parseSceneUrlState(route: string, rawQuery: string): SceneUrlState {
  const query = rawQuery.startsWith("?") ? rawQuery.slice(1) : rawQuery;
  const queryObject = parseSceneQueryToObject(query);
  const search = sceneQueryObjectToSearchParams(queryObject);
  const canonicalQuery = canonicalizeSceneQuery(search).toString().replaceAll("%2C", ",");

  const layersValue = firstParam(queryObject["layers"] as string | string[] | undefined) ?? "none";
  const parsedLayers = parseLayersExpression(layersValue);
  const motion = parseSceneMotion(firstParam(queryObject["motion"] as string | string[] | undefined));

  return {
    route: normalizeRoute(route),
    query: canonicalQuery,
    layerProfile: parseSceneLayerProfile(
      firstParam(queryObject["layerProfile"] as string | string[] | undefined)
    ),
    layersMode: parsedLayers.mode,
    layerIds: sortLayerIds(parsedLayers.layerIds),
    motion,
    debug: firstParam(queryObject["debug"] as string | string[] | undefined) === "1",
    unknownLayerTokens: parsedLayers.unknownLayerTokens
  };
}

export function roundTripSceneUrl(input: BuildSceneUrlInput): SceneUrlState {
  const url = buildCanonicalSceneUrl(input);
  const [path, query = ""] = url.split("?");
  return parseSceneUrlState(path ?? input.route, query);
}

export function resolveSceneQueryPrecedence(input: BuildSceneUrlInput): ResolvedLayerFlags {
  const query = buildCanonicalSceneQuery(input);
  const search = new URLSearchParams(query);
  const object: Record<string, string> = {};

  for (const key of [...new Set(search.keys())]) {
    const value = search.get(key);
    if (value !== null) {
      object[key] = value;
    }
  }

  return resolveLayerFlags(object);
}

export function parseSceneQueryObject(rawQuery: string): SceneQueryObject {
  return parseSceneQueryToObject(rawQuery);
}

export function serializeSceneQueryObject(query: SceneQueryObject): string {
  return serializeSceneQuery(query);
}

export function inferMotionFromResolved(flags: ResolvedLayerFlags): SceneMotionValue {
  return flags.flags["motion.enabled"] ? "on" : "off";
}

export function inferProfileFromResolved(flags: ResolvedLayerFlags): SceneLayerProfile {
  const profile: LayerProfile = flags.profile;
  return profile;
}
