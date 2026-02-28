import type { PitchQueryState } from './types';

export type SearchParamsShape = Record<string, string | ReadonlyArray<string> | undefined>;

function read(value: string | ReadonlyArray<string> | undefined): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

export function resolvePitchQueryState(searchParams: SearchParamsShape | undefined): PitchQueryState {
  const layers = read(searchParams?.layers) ?? 'all';
  const profileInput = read(searchParams?.layerProfile) ?? 'neutral';
  const debugInput = read(searchParams?.debug) ?? '0';

  return {
    layers,
    layerProfile:
      profileInput === 'fx' || profileInput === 'perf' ? profileInput : 'neutral',
    debug: debugInput === '1' ? '1' : '0',
  };
}

export function toReadonlySearchParams(searchParams: SearchParamsShape | undefined): SearchParamsShape {
  return {
    layers: read(searchParams?.layers),
    layerProfile: read(searchParams?.layerProfile),
    layerList: read(searchParams?.layerList),
    debug: read(searchParams?.debug),
  };
}
