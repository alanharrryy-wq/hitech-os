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
      description: "Single command deck for runtime health, route state, and panel readiness.",
      render: () => <ConsoleHomePanel />
    },
    {
      id: "scene",
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
      id: "layers",
      label: "Layer Diagnostics",
      shortLabel: "LYR",
      description: "Requested, resolved, DOM-applied, and missing layer state in one place.",
      render: () => <PitchLayerDebugPanel />
    },
    {
      id: "overlay",
      label: "Visual Overlay",
      shortLabel: "OVR",
      description: "Overlay module slot for future visual guides and hit-area paint.",
      render: () => <PitchVisualOverlayPanel />
    },
    {
      id: "share-look",
      label: "Share Look",
      shortLabel: "SHR",
      description: "Snapshot and replication affordances for scene review flows.",
      render: () => <PitchShareLookPanel />
    },
    {
      id: "runtime",
      label: "Runtime Bridge",
      shortLabel: "RTM",
      description: "Live inspection of diagnostics heartbeat, route state, and bridge payload freshness.",
      render: () => <PitchRuntimeBridgePanel />
    },
    {
      id: "actions",
      label: "Actions",
      shortLabel: "ACT",
      description: "Quick emitters for validation, copying, reset flows, and future automation hooks.",
      render: () => <ConsoleActionsPanel />
    },
    {
      id: "flags",
      label: "Flags",
      shortLabel: "FLG",
      description: "Runtime flags with persistence, document datasets, and event broadcasting.",
      render: () => <ConsoleFlagsPanel />
    },
    {
      id: "perf",
      label: "Perf",
      shortLabel: "FPS",
      description: "Fast telemetry slot for performance smoke checks and visual heaviness clues.",
      render: () => <ConsolePerfPanel />
    },
    {
      id: "layouts",
      label: "Layouts",
      shortLabel: "LAY",
      description: "Persist and restore console arrangements with active tool and flag snapshots.",
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
