\
"use client";

import { useMemo, useState } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function emit(name: string, detail?: unknown) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(name, { detail }));
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

function normalizeQuery(value: string | null | undefined): string {
  if (!value) {
    return "";
  }

  return value.startsWith("?") ? value : `?${value}`;
}

export function ConsoleActionsPanel() {
  const { bindings, bridgeStatus, diagnostics, runtime, refreshDiagnostics, resetFlags } = useDevConsole();
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");
  const [actionState, setActionState] = useState("idle");

  const canonicalPath = useMemo(() => {
    const route = diagnostics?.route ?? runtime?.route ?? "/pitch";
    const query = diagnostics?.query ?? runtime?.query ?? "";
    return `${route}${normalizeQuery(query)}`;
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

  const flash = (value: string) => {
    setActionState(value);
    if (typeof window !== "undefined") {
      window.setTimeout(() => setActionState("idle"), 1400);
    }
  };

  const handleCopy = async () => {
    const ok = await copyText(canonicalPath);
    setCopyState(ok ? "copied" : "failed");
    if (typeof window !== "undefined") {
      window.setTimeout(() => setCopyState("idle"), 1200);
    }
  };

  const handleSnapshot = () => {
    emit("hitech:dev-console:snapshot", {
      ...actionPayload,
      requestedAt: new Date().toISOString()
    });
    flash("snapshot emitted");
  };

  const handleOpenScene = () => {
    emit("hitech:dev-console:open-scene", actionPayload);
    flash("open scene emitted");
  };

  const handleValidateScene = () => {
    emit("hitech:dev-console:validate-scene", {
      ...actionPayload,
      requestedAt: new Date().toISOString()
    });
    const ok = refreshDiagnostics();
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
            Emit Snapshot Event
          </button>
          <button type="button" className={cls("button")} onClick={() => handleOpenScene()}>
            Emit Open Scene
          </button>
          <button type="button" className={cls("button")} onClick={() => handleValidateScene()}>
            Emit Validate Scene
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
