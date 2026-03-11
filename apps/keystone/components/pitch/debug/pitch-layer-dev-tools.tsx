"use client";

import { DevConsole } from "../../dev-console/DevConsole";
import { DevConsoleProvider } from "../../dev-console/DevConsoleContext";
import { ConsoleCoreRuntimeInvariants } from "../../dev-console/core/console-core-runtime-invariants";
import { PitchDevConsoleStabilityHelpers } from "./pitch-dev-console-stability-helpers";
import { PitchRouteSceneBinding } from "./pitch-route-scene-binding";
import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";
import { PitchSceneLookRuntime } from "./pitch-scene-look-runtime";

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
      <PitchSceneLookRuntime />
      <PitchRouteSceneBinding />
      <PitchDevConsoleStabilityHelpers />
      <ConsoleCoreRuntimeInvariants />
      <DevConsole />
    </DevConsoleProvider>
  );
}
