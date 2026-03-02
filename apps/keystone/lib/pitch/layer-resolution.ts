import {
  resolveLayerFlags,
  shouldRenderLayerDebugPanel,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "@hitech/ui-kit";

export interface PitchSearchParamsProps {
  readonly searchParams?: SearchParamsLike;
}

export function resolvePitchLayerFlags(searchParams?: SearchParamsLike) {
  return resolveLayerFlags(searchParams ?? {});
}

export function shouldShowPitchLayerDebug(resolved: ResolvedLayerFlags): boolean {
  return shouldRenderLayerDebugPanel(resolved);
}
