"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { SCENE_STUDIO_REQUEST_DIAGNOSTICS } from "../../lib/scene-studio";
import type {
  DevConsoleBridgeStatus,
  DevConsoleContextValue,
  DevConsoleDiagnosticsSnapshot,
  DevConsoleFlags,
  DevConsoleRuntimeSnapshot,
  SceneStudioBinding
} from "./types";

const DEFAULT_FLAGS: DevConsoleFlags = {
  showGrid: false,
  motionEnabled: false,
  reducedMotion: false,
  showSafeAreas: false,
  showDebugLabels: false
};

const FLAGS_STORAGE_KEY = "keystone.devConsole.flags";
const BRIDGE_BOOT_GRACE_MS = 1800;
const BRIDGE_STALE_MS = 15_000;
const REQUEST_DIAGNOSTICS_TYPE = SCENE_STUDIO_REQUEST_DIAGNOSTICS;
const DIAGNOSTICS_EVENT_NAME = "hitech:dev-console:diagnostics";

const DevConsoleContext = createContext<DevConsoleContextValue | null>(null);

function readFlags(): DevConsoleFlags {
  if (typeof window === "undefined") return DEFAULT_FLAGS;

  try {
    const raw = localStorage.getItem(FLAGS_STORAGE_KEY);
    if (!raw) return DEFAULT_FLAGS;
    return { ...DEFAULT_FLAGS, ...(JSON.parse(raw) as Partial<DevConsoleFlags>) };
  } catch {
    return DEFAULT_FLAGS;
  }
}

function emitFlags(flags: DevConsoleFlags) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("hitech:dev-console:flags", { detail: flags }));
}

function isDiagnosticsSnapshot(value: unknown): value is DevConsoleDiagnosticsSnapshot {
  if (!value || typeof value !== "object") return false;

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.route === "string" &&
    typeof candidate.query === "string" &&
    typeof candidate.timestamp === "string" &&
    !!candidate.resolved &&
    Array.isArray(candidate.enabledLayerIds) &&
    Array.isArray(candidate.missingDataAttributes) &&
    typeof candidate.domDataAttributes === "object"
  );
}

function deriveRuntime(snapshot: DevConsoleDiagnosticsSnapshot | null): DevConsoleRuntimeSnapshot | null {
  if (!snapshot) {
    return null;
  }

  return {
    route: snapshot.route,
    query: snapshot.query,
    timestamp: snapshot.timestamp,
    sceneReady: snapshot.sceneReady,
    diagnosticsAvailable: true,
    enabledLayerIds: snapshot.enabledLayerIds,
    domAttributeCount: Object.keys(snapshot.domDataAttributes).length,
    missingAttributeCount: snapshot.missingDataAttributes.length,
    source: snapshot.resolved.source,
    profile: snapshot.resolved.profile
  };
}

function applyFlagDatasets(flags: DevConsoleFlags) {
  if (typeof document === "undefined") return;

  document.documentElement.dataset["devConsoleGrid"] = String(flags.showGrid);
  document.documentElement.dataset["devConsoleMotion"] = String(flags.motionEnabled);
  document.documentElement.dataset["devConsoleReducedMotion"] = String(flags.reducedMotion);
  document.documentElement.dataset["devConsoleSafeAreas"] = String(flags.showSafeAreas);
  document.documentElement.dataset["devConsoleDebugLabels"] = String(flags.showDebugLabels);
}

export function DevConsoleProvider({ children }: { children: React.ReactNode }) {
  const [sceneStudioBinding, setSceneStudioBinding] = useState<SceneStudioBinding | undefined>(undefined);
  const [flags, setFlags] = useState<DevConsoleFlags>(DEFAULT_FLAGS);
  const [hasRestoredFlags, setHasRestoredFlags] = useState(false);
  const [diagnostics, setDiagnostics] = useState<DevConsoleDiagnosticsSnapshot | null>(null);
  const [bridgeStatus, setBridgeStatus] = useState<DevConsoleBridgeStatus>("booting");
  const [lastDiagnosticsAt, setLastDiagnosticsAt] = useState<string | null>(null);
  const latestRuntimeTsRef = useRef<number>(Date.now());

  useEffect(() => {
    setFlags(readFlags());
    setHasRestoredFlags(true);
  }, []);

  useEffect(() => {
    if (!hasRestoredFlags) return;

    try {
      localStorage.setItem(FLAGS_STORAGE_KEY, JSON.stringify(flags));
    } catch {
      // ignore
    }

    emitFlags(flags);
    applyFlagDatasets(flags);
  }, [flags, hasRestoredFlags]);

  const setDiagnosticsSnapshot = useCallback((snapshot: DevConsoleDiagnosticsSnapshot | null) => {
    setDiagnostics(snapshot);
    const timestamp = snapshot?.timestamp ?? null;
    setLastDiagnosticsAt(timestamp);
    latestRuntimeTsRef.current = Date.now();
    setBridgeStatus(snapshot ? "live" : "idle");

  }, []);

  const refreshDiagnostics = useCallback(() => {
    if (typeof window === "undefined") {
      return false;
    }

    const iframe = document.querySelector<HTMLIFrameElement>('iframe[title="Scene preview"]');
    const targetWindow = iframe?.contentWindow ?? window;

    if (typeof targetWindow.postMessage !== "function") {
      return false;
    }

    const requestId = `dev-console:${Date.now()}`;
    targetWindow.postMessage({ type: REQUEST_DIAGNOSTICS_TYPE, requestId }, window.location.origin);
    setBridgeStatus((previous) => (previous === "idle" ? "booting" : previous));
    return true;
  }, []);


  useEffect(() => {
    if (typeof window === "undefined") return;

    const timer = window.setTimeout(() => {
      if (!diagnostics) {
        refreshDiagnostics();
      }
    }, 220);

    return () => {
      window.clearTimeout(timer);
    };
  }, [diagnostics, refreshDiagnostics]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const onMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) {
        return;
      }

      const payload = (event.data as { payload?: unknown } | null)?.payload;
      if (!isDiagnosticsSnapshot(payload)) {
        return;
      }

      setDiagnosticsSnapshot(payload);
    };

    const onDiagnosticsEvent = (event: Event) => {
      const payload = (event as CustomEvent<unknown>).detail;
      if (!isDiagnosticsSnapshot(payload)) {
        return;
      }

      setDiagnosticsSnapshot(payload);
    };

    const bootTimer = window.setTimeout(() => {
      setBridgeStatus((current) => (current === "booting" ? "idle" : current));
    }, BRIDGE_BOOT_GRACE_MS);

    const staleTimer = window.setInterval(() => {
      const age = Date.now() - latestRuntimeTsRef.current;
      setBridgeStatus((current) => {
        if (current === "idle" || current === "offline") return current;
        return age > BRIDGE_STALE_MS ? "stale" : "live";
      });
    }, 1000);

    window.addEventListener("message", onMessage);
    window.addEventListener(DIAGNOSTICS_EVENT_NAME, onDiagnosticsEvent as EventListener);

    return () => {
      window.clearTimeout(bootTimer);
      window.clearInterval(staleTimer);
      window.removeEventListener("message", onMessage);
      window.removeEventListener(DIAGNOSTICS_EVENT_NAME, onDiagnosticsEvent as EventListener);
    };
  }, [setDiagnosticsSnapshot]);

  const runtime = useMemo(() => deriveRuntime(diagnostics), [diagnostics]);

  const value = useMemo<DevConsoleContextValue>(
    () => ({
      bindings: sceneStudioBinding ? { sceneStudio: sceneStudioBinding } : {},
      setSceneStudioBinding,
      flags,
      setFlags,
      resetFlags: () => setFlags(DEFAULT_FLAGS),
      diagnostics,
      runtime,
      bridgeStatus,
      lastDiagnosticsAt,
      refreshDiagnostics,
      setDiagnosticsSnapshot
    }),
    [bridgeStatus, diagnostics, flags, lastDiagnosticsAt, refreshDiagnostics, runtime, sceneStudioBinding, setDiagnosticsSnapshot]
  );

  return <DevConsoleContext.Provider value={value}>{children}</DevConsoleContext.Provider>;
}

export function useDevConsole() {
  const value = useOptionalDevConsole();
  if (!value) {
    throw new Error("useDevConsole must be used inside DevConsoleProvider");
  }
  return value;
}

export function useOptionalDevConsole() {
  return useContext(DevConsoleContext);
}

export function DevConsoleSceneStudioBinding(props: SceneStudioBinding) {
  const { setSceneStudioBinding } = useDevConsole();

  useEffect(() => {
    setSceneStudioBinding(props);
    return () => setSceneStudioBinding(undefined);
  }, [props, setSceneStudioBinding]);

  return null;
}
