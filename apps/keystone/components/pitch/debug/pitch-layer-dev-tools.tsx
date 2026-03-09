"use client";

import { DevConsole } from "../../dev-console/DevConsole";
import { DevConsoleProvider } from "../../dev-console/DevConsoleContext";
import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";

export interface PitchLayerDevToolsProps {
  readonly visible: boolean;
}

export function PitchLayerDevTools({ visible }: PitchLayerDevToolsProps) {
  if (!visible) {
    return null;
  }

  return (
    <DevConsoleProvider>
      <PitchSceneRuntimeBridge />
      <DevConsole />
    </DevConsoleProvider>
  );
}
