"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";
import {
  DEV_CONSOLE_OPEN_SCENE_EVENT,
  DEV_CONSOLE_SNAPSHOT_EVENT,
  DEV_CONSOLE_VALIDATE_SCENE_EVENT,
  buildCanonicalPath,
  dispatchDevConsoleActionResult,
  normalizeRoutePath
} from "../dev-console-events";

const cls = (name: string) => styles[name] ?? "";

function emit(name: string, detail?: unknown): boolean {
  if (typeof window === "undefined") return false;
  return window.dispatchEvent(new CustomEvent(name, { detail }));
}

function downloadJson(filename: string, payload: unknown) {
  if (typeof window === "undefined") return;
  const text = JSON.stringify(payload, null, 2);
  const blob = new Blob([text], { type: "application/json" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}

async function copyText(text: string): Promise<boolean> {
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  return false;
}

export function ConsoleActionsPanel() {
  const { bindings, bridgeStatus, diagnostics, runtime, refreshDiagnostics, resetFlags, lastActionResult } = useDevConsole();
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");
  const [actionState, setActionState] = useState("idle");
  const fallbackTimersRef = useRef<Record<string, number>>({});

  const canonicalPath = useMemo(() => {
    const route = diagnostics?.route ?? runtime?.route ?? "/pitch";
    const query = diagnostics?.query ?? runtime?.query ?? "";
    return buildCanonicalPath(route, query);
  }, [diagnostics?.query, diagnostics?.route, runtime?.query, runtime?.route]);

  const actionPayload = useMemo(
    () => ({
      canonicalPath,
      sceneId: bindings.sceneStudio?.scene?.id ?? null,
      profile: diagnostics?.resolved.profile ?? runtime?.profile ?? null,
      enabledLayerIds: diagnostics?.enabledLayerIds ?? runtime?.enabledLayerIds ?? [],
      bridgeStatus
    }),
    [bindings.sceneStudio?.scene?.id, bridgeStatus, canonicalPath, diagnostics, runtime]
  );

  useEffect(() => {
    const requestId = lastActionResult?.requestId;
    if (!requestId) {
      return;
    }
    const timer = fallbackTimersRef.current[requestId];
    if (timer) {
      window.clearTimeout(timer);
      delete fallbackTimersRef.current[requestId];
    }
  }, [lastActionResult]);

  useEffect(
    () => () => {
      const timers = Object.values(fallbackTimersRef.current);
      for (const timer of timers) {
        window.clearTimeout(timer);
      }
    },
    []
  );

  const flash = (value: string) => {
    setActionState(value);
    if (typeof window !== "undefined") {
      window.setTimeout(() => setActionState("idle"), 1400);
    }
  };

  const scheduleFallback = (requestId: string, fallback: () => void) => {
    if (typeof window === "undefined") {
      return;
    }
    const timer = window.setTimeout(() => {
      delete fallbackTimersRef.current[requestId];
      fallback();
    }, 260);
    fallbackTimersRef.current[requestId] = timer;
  };

  const handleCopy = async () => {
    const ok = await copyText(canonicalPath);
    setCopyState(ok ? "copied" : "failed");
    if (typeof window !== "undefined") {
      window.setTimeout(() => setCopyState("idle"), 1200);
    }
  };

  const handleSnapshot = () => {
    const requestId = `snapshot:${Date.now()}`;
    const payload = {
      ...actionPayload,
      requestId,
      requestedAt: new Date().toISOString()
    };
    emit(DEV_CONSOLE_SNAPSHOT_EVENT, payload);
    scheduleFallback(requestId, () => {
      downloadJson("dev-console-snapshot.json", payload);
      dispatchDevConsoleActionResult({
        action: "snapshot",
        ok: true,
        message: "Snapshot fallback exported locally",
        requestId,
        at: new Date().toISOString(),
        metadata: { fallback: true, canonicalPath }
      });
    });
    flash("snapshot requested");
  };

  const handleOpenScene = () => {
    const requestId = `open-scene:${Date.now()}`;
    const payload = {
      ...actionPayload,
      requestId
    };
    emit(DEV_CONSOLE_OPEN_SCENE_EVENT, payload);
    scheduleFallback(requestId, () => {
      if (typeof window === "undefined") {
        return;
      }
      window.location.assign(normalizeRoutePath(canonicalPath));
      dispatchDevConsoleActionResult({
        action: "open-scene",
        ok: true,
        message: "Open scene fallback navigated current tab",
        requestId,
        at: new Date().toISOString(),
        metadata: { fallback: true, canonicalPath }
      });
    });
    flash("open scene requested");
  };

  const handleValidateScene = () => {
    const requestId = `validate-scene:${Date.now()}`;
    emit(DEV_CONSOLE_VALIDATE_SCENE_EVENT, {
      ...actionPayload,
      requestId,
      requestedAt: new Date().toISOString()
    });
    const ok = refreshDiagnostics();
    if (!ok) {
      dispatchDevConsoleActionResult({
        action: "validate-scene",
        ok: false,
        message: "Bridge unavailable while requesting diagnostics refresh",
        requestId,
        at: new Date().toISOString(),
        metadata: { canonicalPath, bridgeStatus }
      });
    }
    scheduleFallback(requestId, () => {
      const refreshed = refreshDiagnostics();
      dispatchDevConsoleActionResult({
        action: "validate-scene",
        ok: refreshed,
        message: refreshed
          ? "Validate fallback triggered diagnostics refresh"
          : "Validate fallback could not reach runtime bridge",
        requestId,
        at: new Date().toISOString(),
        metadata: { fallback: true, canonicalPath, bridgeStatus }
      });
    });
    flash(ok ? "validation requested" : "bridge unavailable");
  };

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Quick actions</div>
        <div className={cls("cardHint")}>
          Small but useful emitters. Enough muscle to refresh the console, reset state, and throw signals that future tools can subscribe to.
        </div>
        {actionState !== "idle" ? <div className={cls("cardHint")}>Last action: {actionState}</div> : null}
        {lastActionResult ? (
          <div className={cls("cardHint")}>
            Result: {lastActionResult.action} · {lastActionResult.ok ? "ok" : "fail"} · {lastActionResult.message}
          </div>
        ) : null}

        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
            Refresh Diagnostics
          </button>
          <button type="button" className={cls("button")} onClick={() => void handleCopy()}>
            {copyState === "copied" ? "Copied" : "Copy Route"}
          </button>
          <button type="button" className={cls("button")} onClick={() => resetFlags()}>
            Reset Flags
          </button>
          <button type="button" className={cls("button")} onClick={() => bindings.sceneStudio?.onResetToDefaults()}>
            Reset Scene
          </button>
        </div>

        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={() => handleSnapshot()}>
            Snapshot JSON
          </button>
          <button type="button" className={cls("button")} onClick={() => handleOpenScene()}>
            Open Scene
          </button>
          <button type="button" className={cls("button")} onClick={() => handleValidateScene()}>
            Validate Scene
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Action payload</div>
        <div className={cls("cardHint")}>The console should be a command deck, not a museum. These are the low-friction packets it can ship right now.</div>
        <pre className={cls("codeBox")}>
{JSON.stringify(actionPayload, null, 2)}
        </pre>
      </section>
    </div>
  );
}
