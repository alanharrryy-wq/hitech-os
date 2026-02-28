'use client';

import { createContext, useContext, type PropsWithChildren } from 'react';
import type { LayerResolutionResult } from '../../lib/pitch';

const defaultValue: LayerResolutionResult = {
  mode: 'all',
  profile: 'neutral',
  selectedLayers: [],
  debug: false,
  flags: {
    surfaceBase: false,
    surfaceElevated: false,
    glassEdge: false,
    glassTint: false,
    chartGrid: false,
    chartGlow: false,
    motionMicro: false,
    motionPanels: false,
    perfCompact: false,
    perfDeferred: false,
    debugOutline: false,
    debugMetrics: false,
  },
  queryEcho: {
    layers: 'all',
    layerProfile: 'neutral',
    debug: '0',
    layerList: '',
  },
};

const LayerFlagsContext = createContext<LayerResolutionResult>(defaultValue);

export interface LayerFlagsProviderProps {
  readonly value: LayerResolutionResult;
}

export function LayerFlagsProvider({ value, children }: PropsWithChildren<LayerFlagsProviderProps>) {
  return <LayerFlagsContext.Provider value={value}>{children}</LayerFlagsContext.Provider>;
}

export function useLayerFlags(): LayerResolutionResult {
  return useContext(LayerFlagsContext);
}

export default LayerFlagsProvider;
