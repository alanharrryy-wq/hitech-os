import { useContext } from "react";

import { LayerFlagsContext } from "./LayerFlagsProvider.js";
import { toOnOff, type LayerId } from "./layerIds.js";
import type { LayerFlagsActions, LayerFlagsContextValue } from "./LayerFlagsProvider.js";

export type { LayerFlagsContextValue, LayerFlagsActions };

export function useLayerFlags(): LayerFlagsContextValue {
  return useContext(LayerFlagsContext);
}

export function useLayerFlag(layerId: LayerId): boolean {
  const context = useLayerFlags();
  return context.flags[layerId];
}

export function useLayerOnOff(layerId: LayerId): "on" | "off" {
  return toOnOff(useLayerFlag(layerId));
}

export function useMotionLayerOnOff(): "on" | "off" {
  return useLayerOnOff("motion.enabled");
}

export function useCardBlurLayerOnOff(): "on" | "off" {
  return useLayerOnOff("card.blur");
}
