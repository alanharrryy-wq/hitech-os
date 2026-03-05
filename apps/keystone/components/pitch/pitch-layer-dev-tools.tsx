"use client";

import { useEffect, useState } from "react";
import { LayerDebugPanel } from "@hitech/ui-kit";
import { FloatingWindow } from "../../app/dev/scene-studio/FloatingWindow";
import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";
import { PitchShareLookButton } from "./pitch-share-look-button";
import { PitchVisualSceneOverlay } from "./pitch-visual-scene-overlay";

export interface PitchLayerDevToolsProps {
  readonly visible: boolean;
}

export function PitchLayerDevTools({ visible }: PitchLayerDevToolsProps) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => setHydrated(true), []);

  if (!hydrated) return null;

  if (!visible) {
    return <PitchSceneRuntimeBridge />;
  }

  return (
    <>
      <PitchSceneRuntimeBridge />

      <FloatingWindow
        id="pitch-visual-overlay"
        title="Pitch · Visual Overlay"
        defaultPos={{ x: 580, y: 18 }}
        defaultSize={{ w: 420, h: 280 }}
        minSize={{ w: 300, h: 180 }}
      >
        <PitchVisualSceneOverlay />
      </FloatingWindow>

      <FloatingWindow
        id="pitch-share-look"
        title="Pitch · Share Look"
        defaultPos={{ x: 580, y: 320 }}
        defaultSize={{ w: 420, h: 200 }}
        minSize={{ w: 320, h: 160 }}
      >
        <PitchShareLookButton />
      </FloatingWindow>

      <FloatingWindow
        id="pitch-layer-debug"
        title="Pitch · Layer Debug"
        defaultPos={{ x: 18, y: 540 }}
        defaultSize={{ w: 520, h: 420 }}
        minSize={{ w: 380, h: 260 }}
      >
        <LayerDebugPanel mode="floating" />
      </FloatingWindow>
    </>
  );
}
