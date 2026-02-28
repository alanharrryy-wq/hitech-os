import { createContext, useMemo, type PropsWithChildren, type ReactNode } from "react";

import { resolveLayerFlags, type ResolveLayerFlagsInput, type ResolvedLayerFlags } from "./resolveLayerFlags.js";

function readWindowSearch(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.location.search ?? "";
}

const DEFAULT_RESOLVED_LAYER_FLAGS = resolveLayerFlags({
  search: "",
  isDevelopment: true,
});

export const LayerFlagsContext = createContext<ResolvedLayerFlags>(DEFAULT_RESOLVED_LAYER_FLAGS);

export interface LayerFlagsProviderProps extends PropsWithChildren {
  readonly value?: ResolvedLayerFlags;
  readonly search?: string;
  readonly layers?: ResolveLayerFlagsInput["layers"];
  readonly layerProfile?: ResolveLayerFlagsInput["layerProfile"];
  readonly debug?: ResolveLayerFlagsInput["debug"];
  readonly isDevelopment?: ResolveLayerFlagsInput["isDevelopment"];
}

export function LayerFlagsProvider({
  children,
  value,
  search,
  layers,
  layerProfile,
  debug,
  isDevelopment,
}: LayerFlagsProviderProps): ReactNode {
  const resolved = useMemo(() => {
    if (value) {
      return value;
    }

    return resolveLayerFlags({
      search: search ?? readWindowSearch(),
      layers,
      layerProfile,
      debug,
      isDevelopment,
    });
  }, [debug, isDevelopment, layerProfile, layers, search, value]);

  return <LayerFlagsContext.Provider value={resolved}>{children}</LayerFlagsContext.Provider>;
}
