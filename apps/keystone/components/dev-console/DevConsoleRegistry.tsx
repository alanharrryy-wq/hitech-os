"use client";

import React from "react";
import type { DevConsoleBindings, DevConsoleFlags, DevConsoleToolDefinition, DevConsoleToolId } from "./types";
import { SceneStudioEditorPanel } from "./panels/SceneStudioEditorPanel";
import { PitchLayerDebugPanel } from "./panels/PitchLayerDebugPanel";
import { PitchRuntimeBridgePanel } from "./panels/PitchRuntimeBridgePanel";
import { PitchShareLookPanel } from "./panels/PitchShareLookPanel";
import { PitchVisualOverlayPanel } from "./panels/PitchVisualOverlayPanel";
import { ConsoleHomePanel } from "./panels/ConsoleHomePanel";
import { ConsoleFlagsPanel } from "./panels/ConsoleFlagsPanel";
import { ConsolePerfPanel } from "./panels/ConsolePerfPanel";
import { ConsoleActionsPanel } from "./panels/ConsoleActionsPanel";
import { ConsoleLayoutProfilesPanel } from "./panels/ConsoleLayoutProfilesPanel";
import styles from "./dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

type BuildArgs = {
  bindings: DevConsoleBindings;
  activeTool: DevConsoleToolId;
  setActiveTool: (tool: DevConsoleToolId) => void;
  flags: DevConsoleFlags;
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
};

function unavailableState(title: string, hint: string) {
  return (
    <div className={cls("emptyState")}>
      <div className={cls("cardTitle")}>{title}</div>
      <div className={cls("cardHint")}>{hint}</div>
    </div>
  );
}

export function buildDevConsoleRegistry({
  bindings,
  activeTool,
  setActiveTool,
  flags,
  setFlags
}: BuildArgs): DevConsoleToolDefinition[] {
  return [
    {
      id: "home",
      label: "Home",
      shortLabel: "HOME",
      description: "Control room overview and module slots status.",
      render: () => <ConsoleHomePanel />
    },
    {
      id: "scene",
      label: "Scene Editor",
      shortLabel: "SCN",
      description: "Embedded Scene Studio editor. Uses route-provided binding when available.",
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
            "Wire DevConsoleSceneStudioBinding in the current scene owner component/page. The rest of the console still works."
          )
        )
    },
    {
      id: "layers",
      label: "Layer Debug",
      shortLabel: "LYR",
      description: "Embedded layer debug panel, same debug muscle but inside the single console.",
      render: () => <PitchLayerDebugPanel />
    },
    {
      id: "overlay",
      label: "Visual Overlay",
      shortLabel: "OVR",
      description: "Visual scene overlay, embedded instead of popping its own window.",
      render: () => <PitchVisualOverlayPanel />
    },
    {
      id: "share-look",
      label: "Share Look",
      shortLabel: "SHR",
      description: "Look sharing and replication affordance.",
      render: () => <PitchShareLookPanel />
    },
    {
      id: "runtime",
      label: "Runtime Bridge",
      shortLabel: "RTM",
      description: "Keeps the runtime bridge alive while exposing a dedicated inspection slot.",
      render: () => <PitchRuntimeBridgePanel />
    },
    {
      id: "actions",
      label: "Actions",
      shortLabel: "ACT",
      description: "Quick action emitters for export, snapshot, reset, and future automation.",
      render: () => <ConsoleActionsPanel />
    },
    {
      id: "flags",
      label: "Flags",
      shortLabel: "FLG",
      description: "Runtime flags with persistence and event broadcasting.",
      render: () => <ConsoleFlagsPanel />
    },
    {
      id: "perf",
      label: "Perf",
      shortLabel: "FPS",
      description: "Simple performance telemetry to catch visual heaviness fast.",
      render: () => <ConsolePerfPanel />
    },
    {
      id: "layouts",
      label: "Layouts",
      shortLabel: "LAY",
      description: "Save and restore console layouts with active tool and flags.",
      render: () => (
        <ConsoleLayoutProfilesPanel
          activeTool={activeTool}
          setActiveTool={setActiveTool}
          flags={flags}
          setFlags={setFlags}
        />
      )
    }
  ];
}
