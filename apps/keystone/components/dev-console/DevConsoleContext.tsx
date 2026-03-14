"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import {
  isDiagnosticsResponseMessage
} from "../../lib/scene-studio";
import {
  DEFAULT_SCENE_LOOK_MODEL,
  mergeSceneLookModel,
  normalizeSceneLookModel,
  type SceneLookModel,
  type SceneLookModelPatch
} from "./look/scene-look-model";
import type {
  DevConsoleBridgeMeta,
  DevConsoleBridgeStatus,
  DevConsoleContextValue,
  DevConsoleDiagnosticsSnapshot,
  DevConsoleFlags,
  DevConsoleRuntimeSnapshot,
  SceneStudioBinding
} from "./types";
import {
  DEV_CONSOLE_ACTION_RESULT_EVENT,
  DEV_CONSOLE_DIAGNOSTICS_EVENT,
  DEV_CONSOLE_FLAGS_EVENT,
  type DevConsoleActionResult
} from "./dev-console-events";
import {
  type DiagnosticsRequestTarget,
  requestConsoleDiagnostics
} from "./console-core/console-core-diagnostics";
import { registerConsoleEventListener } from "./console-core/console-core-events";

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
const BRIDGE_SELF_HEAL_RETRY_MS = 3000;

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
  window.dispatchEvent(new CustomEvent(DEV_CONSOLE_FLAGS_EVENT, { detail: flags }));
}

function isDiagnosticsSnapshot(value: unknown): value is DevConsoleDiagnosticsSnapshot {
  if (!value || typeof value !== "object") return false;

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate["route"] === "string" &&
    typeof candidate["query"] === "string" &&
    typeof candidate["timestamp"] === "string" &&
    !!candidate["resolved"] &&
    Array.isArray(candidate["enabledLayerIds"]) &&
    Array.isArray(candidate["missingDataAttributes"]) &&
    typeof candidate["domDataAttributes"] === "object"
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

function sceneLookModelToFlags(model: SceneLookModel): DevConsoleFlags {
  return {
    showGrid: model.overlays.grid,
    motionEnabled: model.motion === "on",
    reducedMotion: model.motion === "reduced",
    showSafeAreas: model.overlays.safeAreas,
    showDebugLabels: model.overlays.debugLabels
  };
}

function mergeSceneLookModelWithFlags(model: SceneLookModel, flags: DevConsoleFlags): SceneLookModel {
  return normalizeSceneLookModel({
    ...model,
    overlays: {
      ...model.overlays,
      grid: flags.showGrid,
      safeAreas: flags.showSafeAreas,
      debugLabels: flags.showDebugLabels
    },
    motion: flags.reducedMotion ? "reduced" : flags.motionEnabled ? "on" : "off"
  });
}

export function DevConsoleProvider({ children }: { children: React.ReactNode }) {
  const [sceneStudioBinding, setSceneStudioBinding] = useState<SceneStudioBinding | undefined>(undefined);
  const [flagsState, setFlagsState] = useState<DevConsoleFlags>(DEFAULT_FLAGS);
  const [sceneLookModel, setSceneLookModel] = useState<SceneLookModel>(DEFAULT_SCENE_LOOK_MODEL);
  const [hasRestoredFlags, setHasRestoredFlags] = useState(false);
  const [diagnostics, setDiagnostics] = useState<DevConsoleDiagnosticsSnapshot | null>(null);
  const [bridgeStatus, setBridgeStatus] = useState<DevConsoleBridgeStatus>("booting");
  const [lastDiagnosticsAt, setLastDiagnosticsAt] = useState<string | null>(null);
  const [lastActionResult, setLastActionResult] = useState<DevConsoleActionResult | null>(null);
  const [bridgeMeta, setBridgeMeta] = useState<DevConsoleBridgeMeta>({
    lastRequestId: null,
    lastRequestAt: null,
    lastRequestTarget: "none",
    lastDiagnosticsSource: null,
    diagnosticsAgeMs: null,
    staleReason: null
  });
  const latestRuntimeTsRef = useRef<number>(Date.now());
  const pendingRequestRef = useRef<{
    requestId: string;
    requestedAtMs: number;
    requestedAtIso: string;
    target: DiagnosticsRequestTarget;
  } | null>(null);
  const lastSelfHealAttemptRef = useRef(0);
  const latestSnapshotKeyRef = useRef<string | null>(null);

  const setFlags = useCallback<React.Dispatch<React.SetStateAction<DevConsoleFlags>>>((next) => {
    setFlagsState((previous) => {
      const resolved = typeof next === "function" ? next(previous) : next;
      setSceneLookModel((current) => mergeSceneLookModelWithFlags(current, resolved));
      return resolved;
    });
  }, []);

  const updateSceneLookModel = useCallback(
    (patch: SceneLookModelPatch | ((previous: SceneLookModel) => SceneLookModelPatch)) => {
      setSceneLookModel((previous) => {
        const next = mergeSceneLookModel(previous, patch);
        setFlagsState(sceneLookModelToFlags(next));
        return next;
      });
    },
    []
  );

  const replaceSceneLookModel = useCallback((next?: SceneLookModel) => {
    const normalized = normalizeSceneLookModel(next ?? DEFAULT_SCENE_LOOK_MODEL);
    setSceneLookModel(normalized);
    setFlagsState(sceneLookModelToFlags(normalized));
  }, []);

  const applyDiagnosticsSnapshot = useCallback(
    (snapshot: DevConsoleDiagnosticsSnapshot | null, source: "message" | "event") => {
      const snapshotKey = snapshot ? `${snapshot.requestId ?? "none"}::${snapshot.timestamp}` : "null";
      if (snapshotKey === latestSnapshotKeyRef.current) {
        return;
      }
      latestSnapshotKeyRef.current = snapshotKey;

      setDiagnostics(snapshot);
      const timestamp = snapshot?.timestamp ?? null;
      setLastDiagnosticsAt(timestamp);
      latestRuntimeTsRef.current = Date.now();
      setBridgeStatus(snapshot ? "live" : "idle");
      setBridgeMeta((previous) => ({
        ...previous,
        lastDiagnosticsSource: source,
        diagnosticsAgeMs: 0,
        staleReason: null
      }));

      const requestId = snapshot?.requestId ?? null;
      if (requestId && pendingRequestRef.current?.requestId === requestId) {
        pendingRequestRef.current = null;
      }
    },
    []
  );

  useEffect(() => {
    const restoredFlags = readFlags();
    setFlagsState(restoredFlags);
    setSceneLookModel((current) => mergeSceneLookModelWithFlags(current, restoredFlags));
    setHasRestoredFlags(true);
  }, []);

  useEffect(() => {
    if (!hasRestoredFlags) return;

    try {
      localStorage.setItem(FLAGS_STORAGE_KEY, JSON.stringify(flagsState));
    } catch {
      // ignore
    }

    emitFlags(flagsState);
    applyFlagDatasets(flagsState);
  }, [flagsState, hasRestoredFlags]);

  const setDiagnosticsSnapshot = useCallback(
    (snapshot: DevConsoleDiagnosticsSnapshot | null) => {
      applyDiagnosticsSnapshot(snapshot, "event");
    },
    [applyDiagnosticsSnapshot]
  );

  const refreshDiagnostics = useCallback(() => {
    const requestResult = requestConsoleDiagnostics();
    const requestAtMs = Date.parse(requestResult.requestedAtIso);
    const target: DiagnosticsRequestTarget = requestResult.target;

    pendingRequestRef.current = {
      requestId: requestResult.requestId,
      requestedAtMs: requestAtMs,
      requestedAtIso: requestResult.requestedAtIso,
      target
    };

    setBridgeMeta((previous) => ({
      ...previous,
      lastRequestId: requestResult.requestId,
      lastRequestAt: requestResult.requestedAtIso,
      lastRequestTarget: target
    }));

    if (target === "none") {
      setBridgeStatus("offline");
      setBridgeMeta((previous) => ({
        ...previous,
        staleReason: "Diagnostics request failed: no postMessage target"
      }));
      return false;
    }

    setBridgeStatus((previous) =>
      previous === "offline" || previous === "idle" || previous === "booting" ? "booting" : previous
    );
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

      if (isDiagnosticsResponseMessage(event.data)) {
        const payload = event.data.payload;
        if (!isDiagnosticsSnapshot(payload)) {
          return;
        }
        applyDiagnosticsSnapshot(payload, "message");
        return;
      }

      const payload = (event.data as { payload?: unknown } | null)?.payload;
      if (isDiagnosticsSnapshot(payload)) {
        applyDiagnosticsSnapshot(payload, "message");
      }
    };

    const onDiagnosticsEvent = (event: Event) => {
      const payload = (event as CustomEvent<unknown>).detail;
      if (!isDiagnosticsSnapshot(payload)) {
        return;
      }

      applyDiagnosticsSnapshot(payload, "event");
    };

    const onActionResult = (event: Event) => {
      const detail = (event as CustomEvent<DevConsoleActionResult>).detail;
      if (!detail || typeof detail !== "object") {
        return;
      }
      setLastActionResult(detail);
    };

    const bootTimer = window.setTimeout(() => {
      setBridgeStatus((current) => (current === "booting" ? "idle" : current));
    }, BRIDGE_BOOT_GRACE_MS);

    const staleTimer = window.setInterval(() => {
      const age = Date.now() - latestRuntimeTsRef.current;
      const pending = pendingRequestRef.current;
      const staleReason =
        age > BRIDGE_STALE_MS
          ? pending
            ? `No diagnostics response for ${Math.round((Date.now() - pending.requestedAtMs) / 1000)}s (request=${pending.requestId}, target=${pending.target})`
            : `No diagnostics heartbeat for ${Math.round(age / 1000)}s`
          : null;

      setBridgeStatus((current) => {
        if (current === "idle" || current === "offline") return current;
        return age > BRIDGE_STALE_MS ? "stale" : "live";
      });
      setBridgeMeta((previous) => ({
        ...previous,
        diagnosticsAgeMs: age,
        staleReason
      }));

      if (age > BRIDGE_STALE_MS) {
        const now = Date.now();
        if (now - lastSelfHealAttemptRef.current >= BRIDGE_SELF_HEAL_RETRY_MS) {
          lastSelfHealAttemptRef.current = now;
          refreshDiagnostics();
        }
      }
    }, 1000);

    window.addEventListener("message", onMessage);
    const disposeDiagnosticsListener = registerConsoleEventListener(
      DEV_CONSOLE_DIAGNOSTICS_EVENT,
      onDiagnosticsEvent as EventListener
    );
    const disposeActionListener = registerConsoleEventListener(
      DEV_CONSOLE_ACTION_RESULT_EVENT,
      onActionResult as EventListener
    );

    return () => {
      window.clearTimeout(bootTimer);
      window.clearInterval(staleTimer);
      window.removeEventListener("message", onMessage);
      disposeDiagnosticsListener();
      disposeActionListener();
    };
  }, [applyDiagnosticsSnapshot, refreshDiagnostics]);

  const runtime = useMemo(() => deriveRuntime(diagnostics), [diagnostics]);

  const value = useMemo<DevConsoleContextValue>(
    () => ({
      bindings: sceneStudioBinding ? { sceneStudio: sceneStudioBinding } : {},
      setSceneStudioBinding,
      flags: flagsState,
      setFlags,
      resetFlags: () => setFlags(DEFAULT_FLAGS),
      diagnostics,
      runtime,
      bridgeStatus,
      bridgeMeta,
      sceneLookModel,
      lastDiagnosticsAt,
      refreshDiagnostics,
      setDiagnosticsSnapshot,
      updateSceneLookModel,
      replaceSceneLookModel,
      lastActionResult
    }),
    [
      bridgeMeta,
      bridgeStatus,
      diagnostics,
      flagsState,
      lastActionResult,
      lastDiagnosticsAt,
      replaceSceneLookModel,
      refreshDiagnostics,
      runtime,
      sceneStudioBinding,
      sceneLookModel,
      setDiagnosticsSnapshot,
      setFlags,
      updateSceneLookModel
    ]
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
