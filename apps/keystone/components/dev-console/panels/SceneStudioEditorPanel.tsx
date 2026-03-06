"use client";

import { SceneStudioEditor, type SceneStudioEditorProps } from "../../scene-studio/scene-studio-editor";

export type SceneStudioEditorPanelProps = SceneStudioEditorProps;

export function SceneStudioEditorPanel(props: SceneStudioEditorPanelProps) {
  return <SceneStudioEditor {...props} />;
}
