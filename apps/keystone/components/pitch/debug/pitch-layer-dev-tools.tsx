\
"use client";

import { DevConsole } from "../../dev-console/DevConsole";
import { DevConsoleProvider } from "../../dev-console/DevConsoleContext";
import { PitchDevConsoleStabilityHelpers } from "./pitch-dev-console-stability-helpers";
import { PitchRouteSceneBinding } from "./pitch-route-scene-binding";
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
      <PitchRouteSceneBinding />
      <PitchDevConsoleStabilityHelpers />
      <DevConsole />
    </DevConsoleProvider>
  );
}
