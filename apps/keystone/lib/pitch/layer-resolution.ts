import {
  ALL_LAYERS,
  LAYER_DATA_ATTRIBUTES,
  createResolvedFromProfile,
  overrideResolvedFlags,
  resolveLayerFlags,
  type LayerId,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "@hitech/ui-kit";

export type PitchSearchParamsInput = SearchParamsLike | Promise<SearchParamsLike> | undefined;

export interface PitchSearchParamsProps {
  readonly searchParams?: PitchSearchParamsInput;
}

export type LayerDomResolution = {
  layerId: LayerId;
  attribute: string;
  enabled: boolean;
};

export async function resolvePitchSearchParams(
  searchParams?: PitchSearchParamsInput
): Promise<SearchParamsLike | undefined> {
  if (!searchParams) {
    return undefined;
  }

  return await Promise.resolve(searchParams);
}

function resolvePitchDefaultLayers(searchParams?: SearchParamsLike): ResolvedLayerFlags {
  const resolved = resolveLayerFlags(searchParams ?? {});
  const hasExplicitUrlOverrides =
    resolved.baseSource !== "default" || resolved.motionSource === "motion";
  const normalized = hasExplicitUrlOverrides
    ? resolved
    : overrideResolvedFlags(createResolvedFromProfile("fx", resolved.debug), {
        "motion.enabled": true
      });

  if (normalized.baseSource === "layers" || normalized.profile === "perf") {
    return normalized;
  }

  if (normalized.motionSource === "motion") {
    return normalized;
  }

  if (normalized.flags["motion.enabled"]) {
    return normalized;
  }

  return overrideResolvedFlags(normalized, {
    "motion.enabled": true
  });
}

export function resolvePitchLayerFlags(searchParams?: SearchParamsLike) {
  const resolved = resolvePitchDefaultLayers(searchParams);

  if (process.env.NODE_ENV !== "production") {
    return resolved;
  }

  const gated: ResolvedLayerFlags = {
    ...resolved,
    debug: false
  };

  return gated;
}

export function resolveEnabledPitchLayerIds(resolved: Pick<ResolvedLayerFlags, "flags">): LayerId[] {
  return ALL_LAYERS.filter((layerId) => Boolean(resolved.flags[layerId]));
}

export function buildLayerDomResolution(
  resolved: Pick<ResolvedLayerFlags, "flags">,
  domDataAttributes: Readonly<Record<string, string>>
): LayerDomResolution[] {
  return ALL_LAYERS.map((layerId) => ({
    layerId,
    attribute: LAYER_DATA_ATTRIBUTES[layerId],
    enabled: Boolean(resolved.flags[layerId]) && domDataAttributes[LAYER_DATA_ATTRIBUTES[layerId]] === "1"
  }));
}
