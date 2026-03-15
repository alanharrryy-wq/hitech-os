"use client";

import { useEffect, useMemo, useState } from "react";
import { useDevConsole } from "./DevConsoleContext";
import { buildDevConsoleRegistry } from "./DevConsoleRegistry";
import type { DevConsoleBridgeStatus, DevConsoleToolId } from "./types";
import {
  CONSOLE_ACTIVE_TOOL_STORAGE_KEY,
  readStoredConsoleTool,
  resetConsoleWindowLayout,
  persistConsoleTool
} from "./core/console-core-layout";
import { useConsoleCoreSingleton } from "./core/console-core-lifecycle";
import { ConsoleCoreShell } from "./core/console-core-shell";

function bridgeTone(status: DevConsoleBridgeStatus) {
  switch (status) {
    case "live":
      return { label: "Bridge live", title: "Diagnostics stream healthy" };
    case "stale":
      return { label: "Bridge stale", title: "Diagnostics stopped updating" };
    case "booting":
      return { label: "Bridge booting", title: "Waiting for first diagnostics heartbeat" };
    case "offline":
      return { label: "Bridge offline", title: "Runtime bridge not detected" };
    default:
      return { label: "Bridge idle", title: "No diagnostics yet" };
  }
}

export function DevConsole() {
  const allowed = useConsoleCoreSingleton("dev-console");
  if (!allowed) {
    return null;
  }

  return <ActualDevConsole />;
}

function ActualDevConsole() {
  const {
    bindings,
    flags,
    setFlags,
    runtime,
    bridgeStatus,
    bridgeMeta,
    lastDiagnosticsAt,
    refreshDiagnostics,
    replaceSceneLookModel
  } = useDevConsole();
  const [activeTool, setActiveTool] = useState<DevConsoleToolId>("home");

  useEffect(() => {
    setActiveTool(readStoredConsoleTool("home"));
  }, []);

  const registry = useMemo(
    () =>
      buildDevConsoleRegistry({
        bindings,
        activeTool,
        setActiveTool,
        flags,
        setFlags
      }),
    [activeTool, bindings, flags, setFlags]
  );

  const active = registry.find((item) => item.id === activeTool) ?? registry[0];
  if (!active) {
    return null;
  }

  const bridgeBadge = bridgeTone(bridgeStatus);
  const runtimeSummary = runtime ? `${runtime.route}${runtime.query ? runtime.query : ""}` : "No runtime snapshot yet";

  const selectTool = (tool: DevConsoleToolId) => {
    setActiveTool(tool);
    persistConsoleTool(tool);
  };

  const clearConsoleStorage = () => {
    const keys = [
      "keystone.floatingWindow.dev-console",
      CONSOLE_ACTIVE_TOOL_STORAGE_KEY,
      "keystone.devConsole.flags",
      "keystone.devConsole.layoutProfiles"
    ];

    try {
      keys.forEach((key) => localStorage.removeItem(key));
    } catch {
      // ignore
    }

    selectTool("home");
    setFlags({
      showGrid: false,
      motionEnabled: false,
      reducedMotion: false,
      showSafeAreas: false,
      showDebugLabels: false
    });
    replaceSceneLookModel();
    resetConsoleWindowLayout("dev-console");
  };

  const statusLine = `${runtimeSummary}${lastDiagnosticsAt ? ` · ${lastDiagnosticsAt}` : ""}${
    bridgeMeta.staleReason ? ` · ${bridgeMeta.staleReason}` : ""
  }`;

  return (
    <ConsoleCoreShell
      registry={registry}
      activeTool={active}
      statusLabel={bridgeBadge.label}
      statusTitle={bridgeMeta.staleReason ? `${bridgeBadge.title}. ${bridgeMeta.staleReason}` : bridgeBadge.title}
      statusLine={statusLine}
      diagnosticsLabel={runtime?.diagnosticsAvailable ? "Runtime synced" : "Runtime awaiting first snapshot"}
      onSelectTool={selectTool}
      onRefreshRuntime={() => refreshDiagnostics()}
      onResetPosition={() => resetConsoleWindowLayout("dev-console")}
      onGoHome={() => selectTool("home")}
      onClearState={clearConsoleStorage}
    />
  );
}
