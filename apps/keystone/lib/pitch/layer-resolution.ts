import {
  createResolvedFromProfile,
  overrideResolvedFlags,
  resolveLayerFlags,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "@hitech/ui-kit";

export type PitchSearchParamsInput = SearchParamsLike | Promise<SearchParamsLike> | undefined;

export interface PitchSearchParamsProps {
  readonly searchParams?: PitchSearchParamsInput;
}

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
