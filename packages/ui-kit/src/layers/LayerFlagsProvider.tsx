"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
  type ReactNode
} from "react";
import { ALL_LAYERS, listEnabledLayers, type LayerId, type LayerProfile } from "./layerIds.js";
import {
  createResolvedFromLayers,
  createResolvedFromProfile,
  resolveLayerFlags,
  type ResolvedLayerFlags,
  type SearchParamsLike
} from "./resolveLayerFlags.js";

export interface LayerFlagsActions {
  readonly setLayer: (layerId: LayerId, enabled: boolean) => void;
  readonly setFlag: (layerId: LayerId, enabled: boolean) => void;
  readonly setAll: (enabled: boolean) => void;
  readonly resetAll: () => void;
  readonly setProfile: (profile: LayerProfile) => void;
  readonly resetNeutral: () => void;
}

export interface LayerFlagsContextValue extends ResolvedLayerFlags, LayerFlagsActions {
  readonly resolved: ResolvedLayerFlags;
  readonly enabledLayers: readonly LayerId[];
}

function toSearchParamsLike({
  search,
  layers,
  layerProfile,
  debug
}: {
  search?: string;
  layers?: string;
  layerProfile?: LayerProfile;
  debug?: boolean;
}): SearchParamsLike {
  const query = search?.startsWith("?") ? search.slice(1) : (search ?? "");
  const fromSearch = new URLSearchParams(query);
  const next: SearchParamsLike = {};

  const layersValue = layers ?? fromSearch.get("layers") ?? undefined;
  const profileValue =
    layerProfile ?? (fromSearch.get("layerProfile") as LayerProfile | null) ?? undefined;
  const debugValue = debug ?? fromSearch.get("debug") === "1";

  if (layersValue !== undefined) {
    next["layers"] = layersValue;
  }
  if (profileValue !== undefined) {
    next["layerProfile"] = profileValue;
  }
  if (debugValue) {
    next["debug"] = "1";
  }

  return next;
}

function readWindowSearch(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.location.search ?? "";
}

function buildInitialResolved(
  value: ResolvedLayerFlags | undefined,
  initialResolved: ResolvedLayerFlags | undefined,
  search: string | undefined,
  layers: string | undefined,
  layerProfile: LayerProfile | undefined,
  debug: boolean | undefined
): ResolvedLayerFlags {
  if (value) return value;
  if (initialResolved) return initialResolved;

  return resolveLayerFlags(
    toSearchParamsLike({
      search: search ?? readWindowSearch(),
      ...(layers !== undefined ? { layers } : {}),
      ...(layerProfile !== undefined ? { layerProfile } : {}),
      ...(debug !== undefined ? { debug } : {})
    })
  );
}

const DEFAULT_RESOLVED_LAYER_FLAGS = resolveLayerFlags({});

const NOOP_ACTIONS: LayerFlagsActions = {
  setLayer: () => {},
  setFlag: () => {},
  setAll: () => {},
  resetAll: () => {},
  setProfile: () => {},
  resetNeutral: () => {}
};

export const LayerFlagsContext = createContext<LayerFlagsContextValue>({
  ...DEFAULT_RESOLVED_LAYER_FLAGS,
  resolved: DEFAULT_RESOLVED_LAYER_FLAGS,
  enabledLayers: listEnabledLayers(DEFAULT_RESOLVED_LAYER_FLAGS.flags),
  ...NOOP_ACTIONS
});

export interface LayerFlagsProviderProps extends PropsWithChildren {
  readonly initialResolved?: ResolvedLayerFlags;
  readonly value?: ResolvedLayerFlags;
  readonly search?: string;
  readonly layers?: string;
  readonly layerProfile?: LayerProfile;
  readonly debug?: boolean;
  readonly isDevelopment?: boolean;
}

export function LayerFlagsProvider({
  children,
  value,
  initialResolved,
  search,
  layers,
  layerProfile,
  debug
}: LayerFlagsProviderProps): ReactNode {
  const computedInitial = useMemo(
    () => buildInitialResolved(value, initialResolved, search, layers, layerProfile, debug),
    [debug, initialResolved, layerProfile, layers, search, value]
  );

  const [resolved, setResolved] = useState<ResolvedLayerFlags>(computedInitial);

  useEffect(() => {
    setResolved(computedInitial);
  }, [computedInitial]);

  const setProfile = useCallback((profile: LayerProfile) => {
    setResolved((prev) => createResolvedFromProfile(profile, prev.debug));
  }, []);

  const setAll = useCallback((enabled: boolean) => {
    setResolved((prev) => createResolvedFromLayers(enabled ? ALL_LAYERS : [], prev.debug));
  }, []);

  const setLayer = useCallback((layerId: LayerId, enabled: boolean) => {
    setResolved((prev) => {
      const currentEnabled = new Set(listEnabledLayers(prev.flags));
      if (enabled) {
        currentEnabled.add(layerId);
      } else {
        currentEnabled.delete(layerId);
      }
      return createResolvedFromLayers([...currentEnabled], prev.debug);
    });
  }, []);

  const resetNeutral = useCallback(() => {
    setResolved((prev) => createResolvedFromProfile("neutral", prev.debug));
  }, []);

  const resetAll = useCallback(() => {
    setAll(false);
  }, [setAll]);

  const contextValue = useMemo<LayerFlagsContextValue>(() => {
    const enabledLayers = listEnabledLayers(resolved.flags);

    return {
      ...resolved,
      resolved,
      enabledLayers,
      setLayer,
      setFlag: setLayer,
      setAll,
      resetAll,
      setProfile,
      resetNeutral
    };
  }, [resolved, resetAll, resetNeutral, setAll, setLayer, setProfile]);

  return <LayerFlagsContext.Provider value={contextValue}>{children}</LayerFlagsContext.Provider>;
}
