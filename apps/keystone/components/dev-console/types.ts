import * as React from "react";
import type { ReactNode } from "react";
import type { LayerFlags, LayerId, ResolvedLayerFlags } from "@hitech/ui-kit";
import type { SceneRecord } from "../../lib/scene-studio";
import type { DevConsoleActionResult } from "./dev-console-events";
import type { SceneLookModel, SceneLookModelPatch } from "./look/scene-look-model";

export type DevConsoleToolId =
  | "home"
  | "scene"
  | "layers"
  | "overlay"
  | "share-look"
  | "runtime"
  | "actions"
  | "flags"
  | "perf"
  | "layouts"
  | "inspect-events"
  | "inspect-snapshot"
  | "compose-look";

export type DevConsoleDomain = "core" | "inspect" | "compose";

export type DevConsoleFlags = {
  showGrid: boolean;
  motionEnabled: boolean;
  reducedMotion: boolean;
  showSafeAreas: boolean;
  showDebugLabels: boolean;
};

export type SceneStudioBinding = {
  scene: SceneRecord | undefined;
  onChange: (scene: SceneRecord) => void;
  onResetToDefaults: () => void;
};

export type DevConsoleBindings = {
  sceneStudio?: SceneStudioBinding;
};

export type DevConsoleToolDefinition = {
  id: DevConsoleToolId;
  domain: DevConsoleDomain;
  label: string;
  shortLabel: string;
  description: string;
  render: () => ReactNode;
};

export type DevConsoleBridgeStatus = "idle" | "booting" | "live" | "stale" | "offline";

export type DevConsoleBridgeMeta = {
  lastRequestId: string | null;
  lastRequestAt: string | null;
  lastRequestTarget: "window" | "window+iframe" | "none";
  lastDiagnosticsSource: "message" | "event" | null;
  diagnosticsAgeMs: number | null;
  staleReason: string | null;
};

export type DevConsoleResolvedSnapshot = Pick<
  ResolvedLayerFlags,
  "source" | "baseSource" | "motionSource" | "profile" | "unknownTokens"
> & {
  flags: LayerFlags;
};

export type DevConsoleDiagnosticsSnapshot = {
  requestId?: string;
  route: string;
  query: string;
  timestamp: string;
  resolved: DevConsoleResolvedSnapshot;
  enabledLayerIds: readonly LayerId[];
  unknownTokens: readonly string[];
  domDataAttributes: Readonly<Record<string, string>>;
  missingDataAttributes: readonly string[];
  sceneReady: string | null;
  userAgent?: string;
};

export type DevConsoleRuntimeSnapshot = {
  route: string;
  query: string;
  timestamp: string;
  sceneReady: string | null;
  diagnosticsAvailable: boolean;
  enabledLayerIds: readonly LayerId[];
  domAttributeCount: number;
  missingAttributeCount: number;
  source: string;
  profile: string;
};

export type DevConsoleContextValue = {
  bindings: DevConsoleBindings;
  setSceneStudioBinding: (binding: SceneStudioBinding | undefined) => void;

  flags: DevConsoleFlags;
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
  resetFlags: () => void;

  diagnostics: DevConsoleDiagnosticsSnapshot | null;
  runtime: DevConsoleRuntimeSnapshot | null;
  bridgeStatus: DevConsoleBridgeStatus;
  bridgeMeta: DevConsoleBridgeMeta;
  sceneLookModel: SceneLookModel;
  lastDiagnosticsAt: string | null;
  refreshDiagnostics: () => boolean;
  setDiagnosticsSnapshot: (snapshot: DevConsoleDiagnosticsSnapshot | null) => void;
  updateSceneLookModel: (patch: SceneLookModelPatch | ((previous: SceneLookModel) => SceneLookModelPatch)) => void;
  replaceSceneLookModel: (next?: SceneLookModel) => void;
  lastActionResult: DevConsoleActionResult | null;
};
