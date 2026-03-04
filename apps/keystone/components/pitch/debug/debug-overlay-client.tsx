"use client";

import { LayerDebugPanel, useLayerFlags } from "@hitech/ui-kit";
import { isPitchDebugOverlayEnabled } from "./overlay-gate";

export function DebugOverlayClient() {
  const { resolved } = useLayerFlags();

  if (!isPitchDebugOverlayEnabled() || !resolved.debug) {
    return null;
  }

  return (
    <div data-pitch-debug-overlay="1">
      <LayerDebugPanel />
    </div>
  );
}
