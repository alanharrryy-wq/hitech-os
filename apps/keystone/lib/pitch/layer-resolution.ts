import { resolveLayerFlags, type SearchParamsLike } from "@hitech/ui-kit";

export interface PitchSearchParamsProps {
  readonly searchParams?: SearchParamsLike | Promise<SearchParamsLike>;
}

export async function resolvePitchLayerFlags(
  searchParams?: SearchParamsLike | Promise<SearchParamsLike>
) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  return resolveLayerFlags(resolvedSearchParams);
}
