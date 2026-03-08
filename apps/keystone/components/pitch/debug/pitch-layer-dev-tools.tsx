"use client";

import { PitchSceneRuntimeBridge } from "./pitch-scene-runtime-bridge";

export interface PitchLayerDevToolsProps {
  readonly visible: boolean;
}

export function PitchLayerDevTools(_props: PitchLayerDevToolsProps) {
  return <PitchSceneRuntimeBridge />;
}