"use client";

import styles from "./scene-studio.module.css";

const cls = (name: string): string => styles[name] ?? "";

export function SceneStudioHelpPanel() {
  return (
    <div className={cls("panelBody")}>
      <p className={cls("subtle")}>
        Scene Studio hotkeys: <code>/</code> focus search, <code>n</code> new scene, <code>Ctrl/Cmd+S</code> save,
        <code>c</code> copy URL, <code>r</code> run visual test.
      </p>
      <ul className={cls("helpList")}>
        <li>Use canonical URLs to reproduce exact scene state in new tabs and Playwright.</li>
        <li>Validate scene to compare requested configuration vs resolved/applied DOM attributes.</li>
        <li>Use export/import to share scene packs with the team.</li>
        <li>Use compare mode to inspect two scenes side-by-side in one workspace.</li>
      </ul>
      <p className={cls("subtle")}>Docs: docs/quality/SCENE_STUDIO.md</p>
      <p className={cls("subtle")}>Docs: docs/quality/UI_IMPROVEMENT_VALIDATION.md</p>
    </div>
  );
}




