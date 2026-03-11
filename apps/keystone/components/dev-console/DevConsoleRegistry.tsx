"use client";

import React from "react";
import type { DevConsoleBindings, DevConsoleFlags, DevConsoleToolDefinition, DevConsoleToolId } from "./types";
import { buildComposeConsolePanels } from "./domains/compose/compose-console-panels";
import { buildInspectConsolePanels } from "./domains/inspect/inspect-console-panels";
import { buildConsoleCoreRegistry } from "./core/console-core-registry";
import { buildCoreConsolePanels } from "./core/core-console-panels";

type BuildArgs = {
  bindings: DevConsoleBindings;
  activeTool: DevConsoleToolId;
  setActiveTool: (tool: DevConsoleToolId) => void;
  flags: DevConsoleFlags;
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
};

export function buildDevConsoleRegistry({
  bindings,
  activeTool,
  setActiveTool,
  flags,
  setFlags
}: BuildArgs): DevConsoleToolDefinition[] {
  const corePanels = buildCoreConsolePanels({ activeTool, setActiveTool, flags, setFlags });
  const inspectPanels = buildInspectConsolePanels();
  const composePanels = buildComposeConsolePanels({ bindings });

  return buildConsoleCoreRegistry({
    corePanels,
    inspectPanels,
    composePanels
  });
}
