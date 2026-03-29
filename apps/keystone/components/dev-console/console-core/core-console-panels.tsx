"use client";

import React from "react";
import type { DevConsoleFlags, DevConsoleToolDefinition, DevConsoleToolId } from "../types";
import { ConsoleActionsPanel } from "../panels/ConsoleActionsPanel";
import { ConsoleHomePanel } from "../panels/ConsoleHomePanel";
import { ConsoleLayoutProfilesPanel } from "../panels/ConsoleLayoutProfilesPanel";

export interface CoreConsolePanelsInput {
  readonly activeTool: DevConsoleToolId;
  readonly setActiveTool: (tool: DevConsoleToolId) => void;
  readonly flags: DevConsoleFlags;
  readonly setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
}

export function buildCoreConsolePanels({
  activeTool,
  setActiveTool,
  flags,
  setFlags
}: CoreConsolePanelsInput): DevConsoleToolDefinition[] {
  return [
    {
      id: "home",
      domain: "core",
      label: "Home",
      shortLabel: "HOME",
      description: "Single command deck for runtime health, route state, and panel readiness.",
      render: () => <ConsoleHomePanel />
    },
    {
      id: "actions",
      domain: "core",
      label: "Actions",
      shortLabel: "ACT",
      description: "Cross-domain command surface with deterministic action result telemetry.",
      render: () => <ConsoleActionsPanel />
    },
    {
      id: "layouts",
      domain: "core",
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
