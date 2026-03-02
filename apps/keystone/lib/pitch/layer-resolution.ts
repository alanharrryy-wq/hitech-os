import {
  resolveLayerFlags,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "@hitech/ui-kit";

export interface PitchSearchParamsProps {
  readonly searchParams?: SearchParamsLike;
}

export function resolvePitchLayerFlags(searchParams?: SearchParamsLike) {
  const resolved = resolveLayerFlags(searchParams ?? {});

  if (process.env.NODE_ENV !== "production") {
    return resolved;
  }

  const gated: ResolvedLayerFlags = {
    ...resolved,
    debug: false
  };

  return gated;
}
