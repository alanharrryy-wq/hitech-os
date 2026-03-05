"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useLayerFlags } from "@hitech/ui-kit";

declare global {
  interface Window {
    __hitechPitchRuntime?: {
      path: string;
      search: string;
      enabledLayers: string[];
      updatedAt: number;
    };
  }
}

export function PitchSceneRuntimeBridge() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const layerState = useLayerFlags();
  const resolved = layerState.resolved ?? layerState;

  useEffect(() => {
    const enabledLayers = Object.entries(resolved.flags)
      .filter(([, enabled]) => enabled)
      .map(([id]) => id);

    window.__hitechPitchRuntime = {
      path: pathname,
      search: searchParams.toString(),
      enabledLayers,
      updatedAt: Date.now()
    };
  }, [pathname, resolved, searchParams]);

  return null;
}
