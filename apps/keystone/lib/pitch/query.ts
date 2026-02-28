import type { LayerName, PitchQueryState } from './types';

export const ALL_LAYER_NAMES: ReadonlyArray<LayerName> = [
  'surfaceBase',
  'surfaceElevated',
  'glassEdge',
  'glassTint',
  'chartGrid',
  'chartGlow',
  'motionMicro',
  'motionPanels',
  'perfCompact',
  'perfDeferred',
  'debugOutline',
  'debugMetrics',
];

export function normalizeLayerList(raw: string | undefined): ReadonlyArray<LayerName> {
  if (!raw) {
    return [];
  }

  const set = new Set<LayerName>();
  const tokens = raw
    .split(',')
    .map((token) => token.trim())
    .filter((token) => token.length > 0);

  for (const token of tokens) {
    if ((ALL_LAYER_NAMES as ReadonlyArray<string>).includes(token)) {
      set.add(token as LayerName);
    }
  }

  return Array.from(set);
}

export function toQueryString(query: PitchQueryState): string {
  const params = new URLSearchParams();
  params.set('layers', query.layers);
  params.set('layerProfile', query.layerProfile);
  params.set('debug', query.debug);
  return params.toString();
}

export function readParam(
  value: string | ReadonlyArray<string> | undefined,
  fallback: string,
): string {
  if (Array.isArray(value)) {
    return value[0] ?? fallback;
  }
  return value ?? fallback;
}

export function isLayerName(value: string): value is LayerName {
  return (ALL_LAYER_NAMES as ReadonlyArray<string>).includes(value);
}
