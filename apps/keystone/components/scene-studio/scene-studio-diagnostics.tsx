"use client";

import { useMemo } from "react";
import {
  validateSceneDiagnostics,
  type SceneDiagnosticsPayload,
  type SceneRecord
} from "../../lib/scene-studio";
import styles from "./scene-studio.module.css";

const cls = (name: string): string => styles[name] ?? "";

export interface SceneStudioDiagnosticsProps {
  readonly scene: SceneRecord | undefined;
  readonly diagnostics: SceneDiagnosticsPayload | null;
}

function downloadJson(fileName: string, value: unknown): void {
  const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function SceneStudioDiagnostics({ scene, diagnostics }: SceneStudioDiagnosticsProps) {
  const validation = useMemo(() => {
    if (!scene || !diagnostics) {
      return null;
    }

    return validateSceneDiagnostics(scene, diagnostics);
  }, [diagnostics, scene]);

  if (!diagnostics) {
    return <p className={cls("subtle")}>Request diagnostics from preview to inspect resolved and applied layer state.</p>;
  }

  const domEntries = Object.entries(diagnostics.domDataAttributes).sort(([left], [right]) =>
    left.localeCompare(right)
  );

  return (
    <div className={cls("panelBody")}>
      <div className={cls("actionsRow")}>
        <button
          type="button"
          className={cls("button")}
          onClick={() =>
            downloadJson(
              `scene-diagnostic-${diagnostics.requestId.replaceAll(":", "-")}.json`,
              diagnostics
            )
          }
        >
          Export Diagnostic Snapshot
        </button>
      </div>

      <div className={cls("kvGrid")}>
        <article className={cls("kvItem")}>
          <p className={cls("kvLabel")}>Resolved Source</p>
          <p className={cls("kvValue")}>{diagnostics.resolved.source}</p>
        </article>
        <article className={cls("kvItem")}>
          <p className={cls("kvLabel")}>Resolved Profile</p>
          <p className={cls("kvValue")}>{diagnostics.resolved.profile}</p>
        </article>
        <article className={cls("kvItem")}>
          <p className={cls("kvLabel")}>Enabled Layers</p>
          <p className={cls("kvValue")}>{diagnostics.enabledLayerIds.length}</p>
        </article>
        <article className={cls("kvItem")}>
          <p className={cls("kvLabel")}>Scene Ready</p>
          <p className={cls("kvValue")}>{diagnostics.sceneReady ?? "0"}</p>
        </article>
      </div>

      <div>
        <p className={cls("legend")}>Unknown Tokens</p>
        <p className={cls("kvValue")}>{diagnostics.unknownTokens.join(", ") || "none"}</p>
      </div>

      <div>
        <p className={cls("legend")}>DOM data-layer-* snapshot</p>
        {domEntries.length === 0 ? (
          <p className={cls("subtle")}>No data-layer-* attributes detected.</p>
        ) : (
          <ul className={cls("sceneList")}>
            {domEntries.map(([key, value]) => (
              <li key={key}>
                <p className={cls("sceneItemMeta")}>
                  {key}={value}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>

      {validation ? (
        <div>
          <p className={cls("legend")}>Validation</p>
          <p className={cls("kvValue")}>{validation.valid ? "PASS" : "WARN"}</p>
          {validation.warnings.map((warning) => (
            <p key={`${warning.code}:${warning.message}`} className={cls("warning")}>
              {warning.code}: {warning.message}
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
}




