import type { ReactNode } from "react";
import type { SceneRecord } from "../../lib/scene-studio";

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
  | "layouts";

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
  label: string;
  shortLabel: string;
  description: string;
  render: () => ReactNode;
};
