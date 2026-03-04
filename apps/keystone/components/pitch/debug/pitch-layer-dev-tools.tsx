"use client";

import { LayerDebugPanel } from "@hitech/ui-kit";
import { PitchShareLookButton } from "./pitch-share-look-button";
import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";
import { PitchVisualSceneOverlay } from "./pitch-visual-scene-overlay";

export interface PitchLayerDevToolsProps {
  readonly visible: boolean;
}

export function PitchLayerDevTools({ visible }: PitchLayerDevToolsProps) {
  if (!visible) {
    return <PitchSceneRuntimeBridge />;
  }

  return (
    <>
      <PitchSceneRuntimeBridge />
      <PitchVisualSceneOverlay />
      <PitchShareLookButton />
      <LayerDebugPanel />
    </>
  );
}
