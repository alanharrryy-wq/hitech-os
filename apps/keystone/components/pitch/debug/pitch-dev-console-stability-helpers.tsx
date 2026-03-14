"use client";

import { useEffect } from "react";
import { ALL_LAYERS, type LayerId } from "@hitech/ui-kit";
import { useOptionalDevConsole } from "../../dev-console/DevConsoleContext";
import {
  DEV_CONSOLE_OPEN_SCENE_EVENT,
  DEV_CONSOLE_SNAPSHOT_EVENT,
  DEV_CONSOLE_VALIDATE_SCENE_EVENT,
  buildCanonicalPath,
  dispatchDevConsoleActionResult,
  normalizeRoutePath
} from "../../dev-console/dev-console-events";
import { registerConsoleEventListener } from "../../dev-console/console-core/console-core-events";

const HEARTBEAT_MS = 7000;
const QUICK_GROUPS: Record<string, readonly LayerId[]> = {
  "STAGE ON": ALL_LAYERS.filter((id) => id.startsWith("stage.")),
  "STAGE OFF": ALL_LAYERS.filter((id) => id.startsWith("stage.")),
  "CARD ON": ALL_LAYERS.filter((id) => id.startsWith("card.")),
  "CARD OFF": ALL_LAYERS.filter((id) => id.startsWith("card.")),
  "INSET ON": ALL_LAYERS.filter((id) => id.startsWith("inset.")),
  "INSET OFF": ALL_LAYERS.filter((id) => id.startsWith("inset.")),
  "MOTION ON": ["motion.enabled"],
  "MOTION OFF": ["motion.enabled"]
};

function copyJson(payload: unknown): void {
  const text = JSON.stringify(payload, null, 2);
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    void navigator.clipboard.writeText(text).catch(() => {
      const blob = new Blob([text], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "dev-console-snapshot.json";
      anchor.click();
      window.URL.revokeObjectURL(url);
    });
    return;
  }

  const blob = new Blob([text], { type: "application/json" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "dev-console-snapshot.json";
  anchor.click();
  window.URL.revokeObjectURL(url);
}

function updateSceneLayers(
  binding: NonNullable<ReturnType<typeof useOptionalDevConsole>>["bindings"]["sceneStudio"],
  command: string
): boolean {
  const scene = binding?.scene;
  if (!scene) {
    return false;
  }

  const group = QUICK_GROUPS[command];
  if (!group || group.length === 0) {
    return false;
  }

  const enable = command.endsWith("ON");
  const existing = new Set<LayerId>(scene.layers?.layerIds ?? []);
  for (const layerId of group) {
    if (enable) {
      existing.add(layerId);
    } else {
      existing.delete(layerId);
    }
  }

  const nextMotion = command === "MOTION ON" ? "on" : command === "MOTION OFF" ? "off" : scene.motion;
  const layerIds = Array.from(existing).sort((left, right) => left.localeCompare(right));
  binding.onChange({
    ...scene,
    motion: nextMotion,
    layers: {
      ...scene.layers,
      mode: layerIds.length > 0 ? "list" : "none",
      layerIds
    },
    updatedAt: new Date().toISOString()
  });
  return true;
}

export function PitchDevConsoleStabilityHelpers() {
  const devConsole = useOptionalDevConsole();

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!devConsole) {
      return;
    }

    const boot = window.setTimeout(() => {
      devConsole.refreshDiagnostics();
    }, 180);

    const heartbeat = window.setInterval(() => {
      if (devConsole.bridgeStatus !== "live") {
        devConsole.refreshDiagnostics();
      }
    }, HEARTBEAT_MS);

    return () => {
      window.clearTimeout(boot);
      window.clearInterval(heartbeat);
    };
  }, [devConsole]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!devConsole) {
      return;
    }
    if (devConsole.bridgeStatus !== "stale") {
      return;
    }

    const retry = window.setTimeout(() => {
      devConsole.refreshDiagnostics();
    }, 250);

    return () => window.clearTimeout(retry);
  }, [devConsole, devConsole?.bridgeStatus]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!devConsole) {
      return;
    }

    const handleSnapshot = (event: Event) => {
      const detail = (event as CustomEvent<Record<string, unknown> | null>).detail ?? {};
      const requestId = typeof detail["requestId"] === "string" ? detail["requestId"] : undefined;
      copyJson({
        generatedAt: new Date().toISOString(),
        canonicalPath: buildCanonicalPath(devConsole.diagnostics?.route ?? devConsole.runtime?.route, devConsole.diagnostics?.query ?? devConsole.runtime?.query),
        bridgeStatus: devConsole.bridgeStatus,
        sceneId: devConsole.bindings.sceneStudio?.scene?.id ?? null,
        diagnostics: devConsole.diagnostics,
        runtime: devConsole.runtime,
        detail
      });
      const result = {
        action: "snapshot",
        ok: true,
        message: "Snapshot exported",
        at: new Date().toISOString(),
        metadata: {
          sceneId: devConsole.bindings.sceneStudio?.scene?.id ?? null
        }
      } as const;
      dispatchDevConsoleActionResult(requestId ? { ...result, requestId } : result);
    };

    const handleOpenScene = (event: Event) => {
      const detail = (event as CustomEvent<{ canonicalPath?: string; requestId?: string } | null>).detail;
      const fallbackPath = buildCanonicalPath(devConsole.diagnostics?.route ?? devConsole.runtime?.route, devConsole.diagnostics?.query ?? devConsole.runtime?.query);
      const nextPath = normalizeRoutePath(detail?.canonicalPath ?? fallbackPath);
      window.location.assign(nextPath);
      const result = {
        action: "open-scene",
        ok: true,
        message: "Navigated to requested scene path",
        at: new Date().toISOString(),
        metadata: {
          nextPath
        }
      } as const;
      dispatchDevConsoleActionResult(detail?.requestId ? { ...result, requestId: detail.requestId } : result);
    };

    const handleValidate = (event: Event) => {
      const detail = (event as CustomEvent<{ requestId?: string } | null>).detail;
      const ok = devConsole.refreshDiagnostics();
      const result = {
        action: "validate-scene",
        ok,
        message: ok ? "Diagnostics refresh requested" : "Unable to contact runtime bridge",
        at: new Date().toISOString()
      } as const;
      dispatchDevConsoleActionResult(detail?.requestId ? { ...result, requestId: detail.requestId } : result);
    };

    const disposeSnapshotListener = registerConsoleEventListener(
      DEV_CONSOLE_SNAPSHOT_EVENT,
      handleSnapshot as EventListener
    );
    const disposeOpenSceneListener = registerConsoleEventListener(
      DEV_CONSOLE_OPEN_SCENE_EVENT,
      handleOpenScene as EventListener
    );
    const disposeValidateSceneListener = registerConsoleEventListener(
      DEV_CONSOLE_VALIDATE_SCENE_EVENT,
      handleValidate as EventListener
    );

    return () => {
      disposeSnapshotListener();
      disposeOpenSceneListener();
      disposeValidateSceneListener();
    };
  }, [devConsole]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!devConsole?.bindings.sceneStudio) {
      return;
    }

    const onClickCapture = (event: Event) => {
      const target = event.target as HTMLElement | null;
      const button = target?.closest("button");
      if (!button) {
        return;
      }

      const raw = button.getAttribute("data-dev-console-scene-command");
      if (!raw) {
        return;
      }
      const label = raw.trim().toUpperCase();
      if (!(label in QUICK_GROUPS)) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();
      const ok = updateSceneLayers(devConsole.bindings.sceneStudio, label);
      dispatchDevConsoleActionResult({
        action: "toggle-scene-group",
        ok,
        message: ok ? `Applied ${label}` : `Failed ${label}`,
        at: new Date().toISOString(),
        metadata: { command: label }
      });
    };

    document.addEventListener("click", onClickCapture, true);
    return () => document.removeEventListener("click", onClickCapture, true);
  }, [devConsole, devConsole?.bindings.sceneStudio]);

  return null;
}
