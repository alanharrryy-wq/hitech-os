\
"use client";

import { useEffect } from "react";
import { useOptionalDevConsole } from "../../dev-console/DevConsoleContext";

const HEARTBEAT_MS = 4000;
const QUICK_GROUPS: Record<string, readonly string[]> = {
  "STAGE ON": ["stage.haze", "stage.noise", "stage.horizon", "stage.vignette", "stage.scanlines"],
  "STAGE OFF": ["stage.haze", "stage.noise", "stage.horizon", "stage.vignette", "stage.scanlines"],
  "CARD ON": ["card.blur", "card.specular", "card.shadowAmbient", "frame.bezel", "card.innerStroke", "card.grain"],
  "CARD OFF": ["card.blur", "card.specular", "card.shadowAmbient", "frame.bezel", "card.innerStroke", "card.grain"],
  "INSET ON": ["inset.shadow"],
  "INSET OFF": ["inset.shadow"],
  "MOTION ON": ["motion.enabled"],
  "MOTION OFF": ["motion.enabled"]
};

function normalizePath(path: string | null | undefined): string {
  if (!path) {
    return "/pitch";
  }

  return path.startsWith("/") ? path : `/${path}`;
}

function normalizeQuery(query: string | null | undefined): string {
  if (!query) {
    return "";
  }

  return query.startsWith("?") ? query.slice(1) : query;
}

function buildCanonicalPath(route: string | null | undefined, query: string | null | undefined): string {
  const normalizedRoute = normalizePath(route);
  const normalizedQuery = normalizeQuery(query);
  return normalizedQuery ? `${normalizedRoute}?${normalizedQuery}` : normalizedRoute;
}

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

function updateSceneLayers(binding: NonNullable<ReturnType<typeof useOptionalDevConsole>>["bindings"]["sceneStudio"], command: string) {
  const scene = binding?.scene;
  if (!scene) {
    return;
  }

  const group = QUICK_GROUPS[command];
  if (!group || group.length === 0) {
    return;
  }

  const enable = command.endsWith("ON");
  const existing = new Set(scene.layers?.layerIds ?? []);
  for (const layerId of group) {
    if (enable) {
      existing.add(layerId);
    } else {
      existing.delete(layerId);
    }
  }

  const nextMotion = command === "MOTION ON" ? "on" : command === "MOTION OFF" ? "off" : scene.motion;
  binding.onChange({
    ...scene,
    motion: nextMotion,
    layers: {
      ...scene.layers,
      layerIds: Array.from(existing)
    },
    updatedAt: new Date().toISOString()
  });
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
      devConsole.refreshDiagnostics();
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
      copyJson({
        generatedAt: new Date().toISOString(),
        canonicalPath: buildCanonicalPath(devConsole.diagnostics?.route ?? devConsole.runtime?.route, devConsole.diagnostics?.query ?? devConsole.runtime?.query),
        bridgeStatus: devConsole.bridgeStatus,
        sceneId: devConsole.bindings.sceneStudio?.scene?.id ?? null,
        diagnostics: devConsole.diagnostics,
        runtime: devConsole.runtime,
        detail
      });
    };

    const handleOpenScene = (event: Event) => {
      const detail = (event as CustomEvent<{ canonicalPath?: string } | null>).detail;
      const fallbackPath = buildCanonicalPath(devConsole.diagnostics?.route ?? devConsole.runtime?.route, devConsole.diagnostics?.query ?? devConsole.runtime?.query);
      const nextPath = normalizePath(detail?.canonicalPath ?? fallbackPath);
      window.open(nextPath, "_blank", "noopener,noreferrer");
    };

    const handleValidate = () => {
      devConsole.refreshDiagnostics();
    };

    window.addEventListener("hitech:dev-console:snapshot", handleSnapshot as EventListener);
    window.addEventListener("hitech:dev-console:open-scene", handleOpenScene as EventListener);
    window.addEventListener("hitech:dev-console:validate-scene", handleValidate as EventListener);

    return () => {
      window.removeEventListener("hitech:dev-console:snapshot", handleSnapshot as EventListener);
      window.removeEventListener("hitech:dev-console:open-scene", handleOpenScene as EventListener);
      window.removeEventListener("hitech:dev-console:validate-scene", handleValidate as EventListener);
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

      const label = (button.textContent ?? "").trim().toUpperCase();
      if (!(label in QUICK_GROUPS)) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();
      updateSceneLayers(devConsole.bindings.sceneStudio, label);
    };

    document.addEventListener("click", onClickCapture, true);
    return () => document.removeEventListener("click", onClickCapture, true);
  }, [devConsole, devConsole?.bindings.sceneStudio]);

  return null;
}
