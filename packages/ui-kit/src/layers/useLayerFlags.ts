"use client";

import { createContext, useContext } from "react";
import {
  ALL_LAYERS,
  createAllLayersOff,
  type LayerFlags,
  type LayerId,
  type LayerProfile
} from "./layerIds.js";
import { resolveLayerFlags, type ResolvedLayerFlags } from "./resolveLayerFlags.js";

export interface LayerFlagsActions {
  readonly setLayer: (id: LayerId, on: boolean) => void;
  readonly setAll: (on: boolean) => void;
  readonly setProfile: (profile: LayerProfile) => void;
  readonly setMotion: (on: boolean) => void;
  readonly resetNeutral: () => void;
}

export interface LayerFlagsContextValue extends LayerFlagsActions {
  readonly resolved: ResolvedLayerFlags;
  readonly flags: LayerFlags;
  readonly enabledLayers: readonly LayerId[];
}

const DEFAULT_RESOLVED = resolveLayerFlags({});
const NOOP = () => {
  return;
};

export const DEFAULT_LAYER_FLAGS_CONTEXT: LayerFlagsContextValue = {
  resolved: DEFAULT_RESOLVED,
  flags: createAllLayersOff(),
  enabledLayers: [],
  setLayer: NOOP,
  setAll: NOOP,
  setProfile: NOOP,
  setMotion: NOOP,
  resetNeutral: NOOP
};

export const LayerFlagsContext = createContext<LayerFlagsContextValue>(DEFAULT_LAYER_FLAGS_CONTEXT);

export function useLayerFlags(): LayerFlagsContextValue {
  return useContext(LayerFlagsContext);
}

export function extractEnabledLayerIds(flags: LayerFlags): LayerId[] {
  return ALL_LAYERS.filter((id) => flags[id]);
}
