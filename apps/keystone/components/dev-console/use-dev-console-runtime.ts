"use client";

import { useMemo } from "react";
import { useDevConsole } from "./DevConsoleContext";
import type {
  DevConsoleDiagnosticsSnapshot,
  DevConsoleRuntimeSnapshot,
  DevConsoleBridgeStatus
} from "./types";

export interface UseDevConsoleRuntimeResult {
  readonly diagnostics: DevConsoleDiagnosticsSnapshot | null;
  readonly runtime: DevConsoleRuntimeSnapshot | null;
  readonly bridgeStatus: DevConsoleBridgeStatus;
  readonly lastDiagnosticsAt: string | null;
  readonly hasDiagnostics: boolean;
  readonly isBridgeHealthy: boolean;
  readonly enabledLayerCount: number;
  readonly missingAttributeCount: number;
  readonly domAttributeCount: number;
  readonly refreshDiagnostics: () => boolean;
}

export function useDevConsoleRuntime(): UseDevConsoleRuntimeResult {
  const { diagnostics, runtime, bridgeStatus, lastDiagnosticsAt, refreshDiagnostics } = useDevConsole();

  return useMemo(
    () => ({
      diagnostics,
      runtime,
      bridgeStatus,
      lastDiagnosticsAt,
      hasDiagnostics: Boolean(diagnostics),
      isBridgeHealthy: bridgeStatus === "live",
      enabledLayerCount: runtime?.enabledLayerIds.length ?? diagnostics?.enabledLayerIds.length ?? 0,
      missingAttributeCount:
        runtime?.missingAttributeCount ?? diagnostics?.missingDataAttributes.length ?? 0,
      domAttributeCount: runtime?.domAttributeCount ?? Object.keys(diagnostics?.domDataAttributes ?? {}).length,
      refreshDiagnostics
    }),
    [bridgeStatus, diagnostics, lastDiagnosticsAt, refreshDiagnostics, runtime]
  );
}
