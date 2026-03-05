import { resolveLayerFlags, type SearchParamsLike } from "@hitech/ui-kit";

export interface PitchSearchParamsProps {
  readonly searchParams?: SearchParamsLike;
}

export function resolvePitchLayerFlags(searchParams?: SearchParamsLike) {
  return resolveLayerFlags(searchParams ?? {});
}
