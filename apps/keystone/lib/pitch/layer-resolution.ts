import { resolveFeatureFlags, type FeatureFlags } from '@hitech/contracts';
import { ALL_LAYER_NAMES, isLayerName, normalizeLayerList, readParam } from './query';
import type { LayerFlags, LayerName, LayerProfile, LayerResolutionResult } from './types';

const PROFILE_PRESETS: Readonly<Record<LayerProfile, ReadonlyArray<LayerName>>> = {
  neutral: ['surfaceBase', 'surfaceElevated', 'chartGrid', 'perfCompact'],
  fx: [
    'surfaceBase',
    'surfaceElevated',
    'glassEdge',
    'glassTint',
    'chartGrid',
    'chartGlow',
    'motionMicro',
    'motionPanels',
  ],
  perf: ['surfaceBase', 'chartGrid', 'perfCompact', 'perfDeferred'],
};

function buildFlags(enabled: ReadonlyArray<LayerName>): LayerFlags {
  const map = new Map<LayerName, boolean>();
  for (const layer of ALL_LAYER_NAMES) {
    map.set(layer, enabled.includes(layer));
  }

  return {
    surfaceBase: map.get('surfaceBase') ?? false,
    surfaceElevated: map.get('surfaceElevated') ?? false,
    glassEdge: map.get('glassEdge') ?? false,
    glassTint: map.get('glassTint') ?? false,
    chartGrid: map.get('chartGrid') ?? false,
    chartGlow: map.get('chartGlow') ?? false,
    motionMicro: map.get('motionMicro') ?? false,
    motionPanels: map.get('motionPanels') ?? false,
    perfCompact: map.get('perfCompact') ?? false,
    perfDeferred: map.get('perfDeferred') ?? false,
    debugOutline: map.get('debugOutline') ?? false,
    debugMetrics: map.get('debugMetrics') ?? false,
  };
}

export function resolveLayerFlags(
  searchParams:
    | Record<string, string | ReadonlyArray<string> | undefined>
    | URLSearchParams
    | undefined,
): LayerResolutionResult {
  const rawLayers =
    searchParams instanceof URLSearchParams
      ? searchParams.get('layers') ?? 'all'
      : readParam(searchParams?.layers, 'all');

  const rawProfile =
    searchParams instanceof URLSearchParams
      ? searchParams.get('layerProfile') ?? 'neutral'
      : readParam(searchParams?.layerProfile, 'neutral');

  const rawDebug =
    searchParams instanceof URLSearchParams
      ? searchParams.get('debug') ?? '0'
      : readParam(searchParams?.debug, '0');

  const rawList =
    searchParams instanceof URLSearchParams
      ? searchParams.get('layerList') ?? ''
      : readParam(searchParams?.layerList, '');

  const profile: LayerProfile = rawProfile === 'fx' || rawProfile === 'perf' ? rawProfile : 'neutral';

  let mode: 'none' | 'all' | 'list' = 'all';
  if (rawLayers === 'none') {
    mode = 'none';
  } else if (rawLayers === 'list') {
    mode = 'list';
  } else if (rawLayers === 'all') {
    mode = 'all';
  } else if (rawLayers.includes(',')) {
    mode = 'list';
  }

  const baseLayers = [...PROFILE_PRESETS[profile]];
  let selectedLayers: ReadonlyArray<LayerName>;

  if (mode === 'none') {
    selectedLayers = [];
  } else if (mode === 'all') {
    selectedLayers = [...ALL_LAYER_NAMES];
  } else {
    const listSource = rawLayers === 'list' ? rawList : rawLayers;
    const explicit = normalizeLayerList(listSource);
    selectedLayers = explicit.length > 0 ? explicit : baseLayers;
  }

  const debug = rawDebug === '1';
  if (debug) {
    selectedLayers = Array.from(new Set([...selectedLayers, 'debugOutline', 'debugMetrics']));
  }

  return {
    mode,
    profile,
    selectedLayers,
    debug,
    flags: buildFlags(selectedLayers),
    queryEcho: {
      layers: rawLayers,
      layerProfile: profile,
      debug: debug ? '1' : '0',
      layerList: mode === 'list' ? selectedLayers.join(',') : '',
    },
  };
}

export function deriveFeatureFlagsFromLayers(result: LayerResolutionResult): FeatureFlags {
  return resolveFeatureFlags({
    enableAiExecution: result.flags.perfDeferred,
    enableCapabilitiesProxy: result.flags.surfaceElevated,
    enableExperimentalUi: result.flags.glassTint || result.flags.chartGlow,
    enableHealthDashboard: result.flags.debugMetrics,
  });
}

export function layerFlagsToClassTokens(flags: LayerFlags): string {
  const tokens: string[] = [];
  for (const name of ALL_LAYER_NAMES) {
    if (flags[name]) {
      tokens.push(`layer-${name}`);
    }
  }
  return tokens.join(' ');
}

export function filterKnownLayers(values: ReadonlyArray<string>): ReadonlyArray<LayerName> {
  return values.filter((value): value is LayerName => isLayerName(value));
}
