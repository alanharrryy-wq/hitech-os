"use client";

import type { DevConsoleToolDefinition } from "../../types";
import { PitchLayerDebugPanel } from "../../panels/PitchLayerDebugPanel";
import { PitchRuntimeBridgePanel } from "../../panels/PitchRuntimeBridgePanel";
import { ConsolePerfPanel } from "../../panels/ConsolePerfPanel";
import { InspectEventMonitorPanel } from "./InspectEventMonitorPanel";
import { InspectSnapshotViewerPanel } from "./InspectSnapshotViewerPanel";

export function buildInspectConsolePanels(): DevConsoleToolDefinition[] {
  return [
    {
      id: "runtime",
      domain: "inspect",
      label: "Runtime Bridge",
      shortLabel: "RTM",
      description: "Live inspection of diagnostics heartbeat, route state, and bridge payload freshness.",
      render: () => <PitchRuntimeBridgePanel />
    },
    {
      id: "layers",
      domain: "inspect",
      label: "Layer Diagnostics",
      shortLabel: "LYR",
      description: "Requested, resolved, DOM-applied, and missing layer state in one place.",
      render: () => <PitchLayerDebugPanel />
    },
    {
      id: "perf",
      domain: "inspect",
      label: "Perf",
      shortLabel: "FPS",
      description: "Fast telemetry slot for performance smoke checks and visual heaviness clues.",
      render: () => <ConsolePerfPanel />
    },
    {
      id: "inspect-events",
      domain: "inspect",
      label: "Event Monitor",
      shortLabel: "EVT",
      description: "Inspect event topology and listener presence with runtime contract checks.",
      render: () => <InspectEventMonitorPanel />
    },
    {
      id: "inspect-snapshot",
      domain: "inspect",
      label: "Snapshot Viewer",
      shortLabel: "SNP",
      description: "Read-only runtime and diagnostics payload inspection.",
      render: () => <InspectSnapshotViewerPanel />
    }
  ];
}
