import {
  createResolvedFromProfile,
  overrideResolvedFlags,
  resolveLayerFlags,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "@hitech/ui-kit";

export interface PitchSearchParamsProps {
  readonly searchParams?: SearchParamsLike;
}

function resolvePitchDefaultLayers(searchParams?: SearchParamsLike): ResolvedLayerFlags {
  const resolved = resolveLayerFlags(searchParams ?? {});
  const normalized =
    resolved.source === "default" ? createResolvedFromProfile("fx", resolved.debug) : resolved;

  if (normalized.source === "layers" || normalized.profile === "perf") {
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
