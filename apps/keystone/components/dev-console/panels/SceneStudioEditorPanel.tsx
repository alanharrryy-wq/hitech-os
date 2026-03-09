"use client";

import { SceneStudioEditor, type SceneStudioEditorProps } from "../../scene-studio/scene-studio-editor";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

export type SceneStudioEditorPanelProps = SceneStudioEditorProps;

export function SceneStudioEditorPanel(props: SceneStudioEditorPanelProps) {
  if (!props.scene) {
    return (
      <div className={cls("emptyState")}>
        <div className={cls("cardTitle")}>Scene binding unavailable</div>
        <div className={cls("cardHint")}>
          The SCN slot is wired, but there is no current scene bound into the console yet.
        </div>
      </div>
    );
  }

  return <SceneStudioEditor {...props} />;
}
