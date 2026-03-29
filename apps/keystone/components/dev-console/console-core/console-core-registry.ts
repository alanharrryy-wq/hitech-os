"use client";

import type { DevConsoleToolDefinition } from "../types";
import { createConsoleCoreLogger } from "./console-core-logger";

const logger = createConsoleCoreLogger("Registry");

export interface ConsoleCoreRegistryInput {
  readonly corePanels: readonly DevConsoleToolDefinition[];
  readonly inspectPanels: readonly DevConsoleToolDefinition[];
  readonly composePanels: readonly DevConsoleToolDefinition[];
}

export function buildConsoleCoreRegistry(input: ConsoleCoreRegistryInput): DevConsoleToolDefinition[] {
  const registry = [...input.corePanels, ...input.inspectPanels, ...input.composePanels];
  const seenIds = new Set<string>();

  for (const panel of registry) {
    if (seenIds.has(panel.id)) {
      logger.error("Duplicate panel id detected", { panelId: panel.id, domain: panel.domain });
      continue;
    }
    seenIds.add(panel.id);
  }

  return registry;
}
