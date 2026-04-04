"use client";

import { createContext, useContext, useMemo, type PropsWithChildren } from "react";
import {
  SceneStudioEditor as BaseSceneStudioEditor,
  type SceneStudioEditorProps
} from "../../../components/scene-studio/scene-studio-editor";
import { useSceneStudioState } from "../../../components/scene-studio/use-scene-studio-state";
import type { SceneRecord } from "../../../lib/scene-studio";

interface SceneStudioRuntimeValue {
  readonly currentScene: SceneRecord | undefined;
  readonly updateScene: (scene: SceneRecord) => void;
  readonly resetSceneToDefaults: () => void;
}

const SceneStudioRuntimeContext = createContext<SceneStudioRuntimeValue | null>(null);

export type { SceneStudioEditorProps };

export function SceneStudioEditor(props: SceneStudioEditorProps) {
  return <BaseSceneStudioEditor {...props} />;
}

export function SceneStudioRuntimeProvider({ children }: PropsWithChildren) {
  const { draftScene, updateDraft, resetSelectedSceneToDefaults } = useSceneStudioState();

  const value = useMemo<SceneStudioRuntimeValue>(
    () => ({
      currentScene: draftScene,
      updateScene: updateDraft,
      resetSceneToDefaults: resetSelectedSceneToDefaults
    }),
    [draftScene, resetSelectedSceneToDefaults, updateDraft]
  );

  return <SceneStudioRuntimeContext.Provider value={value}>{children}</SceneStudioRuntimeContext.Provider>;
}

export function useSceneStudioRuntime(): SceneStudioRuntimeValue {
  const value = useContext(SceneStudioRuntimeContext);
  if (!value) {
    throw new Error("useSceneStudioRuntime must be used inside SceneStudioRuntimeProvider");
  }

  return value;
}

export function SceneStudioEditorPanel() {
  const { currentScene, updateScene, resetSceneToDefaults } = useSceneStudioRuntime();

  return (
    <SceneStudioEditor
      scene={currentScene}
      onChange={updateScene}
      onResetToDefaults={resetSceneToDefaults}
    />
  );
}
