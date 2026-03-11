"use client";

import type { DevConsoleBindings, DevConsoleToolDefinition } from "../../types";
import { SceneStudioEditorPanel } from "../../panels/SceneStudioEditorPanel";
import { ConsoleFlagsPanel } from "../../panels/ConsoleFlagsPanel";
import { PitchShareLookPanel } from "../../panels/PitchShareLookPanel";
import { PitchVisualOverlayPanel } from "../../panels/PitchVisualOverlayPanel";
import { ComposeSceneLookPanel } from "./ComposeSceneLookPanel";
import styles from "../../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function unavailableState(title: string, hint: string) {
  return (
    <div className={cls("emptyState")}>
      <div className={cls("cardTitle")}>{title}</div>
      <div className={cls("cardHint")}>{hint}</div>
    </div>
  );
}

export interface ComposeConsolePanelsInput {
  readonly bindings: DevConsoleBindings;
}

export function buildComposeConsolePanels({ bindings }: ComposeConsolePanelsInput): DevConsoleToolDefinition[] {
  return [
    {
      id: "scene",
      domain: "compose",
      label: "Scene Editor",
      shortLabel: "SCN",
      description: "Embedded Scene Studio editor bound to the current route owner when available.",
      render: () =>
        bindings.sceneStudio ? (
          <SceneStudioEditorPanel
            scene={bindings.sceneStudio.scene}
            onChange={bindings.sceneStudio.onChange}
            onResetToDefaults={bindings.sceneStudio.onResetToDefaults}
          />
        ) : (
          unavailableState(
            "Scene binding unavailable",
            "Wire DevConsoleSceneStudioBinding in the owning page or editor wrapper. Runtime and diagnostics panels still work."
          )
        )
    },
    {
      id: "compose-look",
      domain: "compose",
      label: "Compose Look",
      shortLabel: "LOOK",
      description: "Canonical SceneLookModel editor for controlled visual composition changes.",
      render: () => <ComposeSceneLookPanel />
    },
    {
      id: "overlay",
      domain: "compose",
      label: "Visual Overlay",
      shortLabel: "OVR",
      description: "Overlay module slot for future visual guides and hit-area paint.",
      render: () => <PitchVisualOverlayPanel />
    },
    {
      id: "share-look",
      domain: "compose",
      label: "Share Look",
      shortLabel: "SHR",
      description: "Snapshot and replication affordances for scene review flows.",
      render: () => <PitchShareLookPanel />
    },
    {
      id: "flags",
      domain: "compose",
      label: "Flags",
      shortLabel: "FLG",
      description: "Runtime flags with persistence, document datasets, and event broadcasting.",
      render: () => <ConsoleFlagsPanel />
    }
  ];
}
