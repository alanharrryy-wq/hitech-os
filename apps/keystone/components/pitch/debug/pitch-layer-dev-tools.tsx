"use client";

import { LayerDebugPanel } from "@hitech/ui-kit";
import { PitchShareLookButton } from "./pitch-share-look-button";
import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";
import { PitchVisualSceneOverlay } from "./pitch-visual-scene-overlay";
import { useOptionalDevConsole } from "../../dev-console/DevConsoleContext";

export interface PitchLayerDevToolsProps {
  readonly visible: boolean;
}

export function PitchLayerDevTools({ visible }: PitchLayerDevToolsProps) {
  const devConsole = useOptionalDevConsole();

  // When the single Dev Console is mounted, disable legacy multi-window HUD mounts.
  if (devConsole) {
    return <PitchSceneRuntimeBridge />;
  }

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
