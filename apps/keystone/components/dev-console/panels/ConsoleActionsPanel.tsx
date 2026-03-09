"use client";

import { useState } from "react";
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

export function ConsoleActionsPanel() {
  const { bindings, diagnostics, runtime, refreshDiagnostics, resetFlags } = useDevConsole();
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");

  const canonicalPath = `${diagnostics?.route ?? runtime?.route ?? "/pitch"}${diagnostics?.query ?? runtime?.query ?? ""}`;

  const handleCopy = async () => {
    const ok = await copyText(canonicalPath);
    setCopyState(ok ? "copied" : "failed");
    window.setTimeout(() => setCopyState("idle"), 1200);
  };

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Quick actions</div>
        <div className={cls("cardHint")}>
          Small but useful emitters. Enough muscle to refresh the console, reset state, and throw signals that future tools can subscribe to.
        </div>

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
          <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:snapshot", { canonicalPath })}>
            Emit Snapshot Event
          </button>
          <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:open-scene", { canonicalPath })}>
            Emit Open Scene
          </button>
          <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:validate-scene", { canonicalPath })}>
            Emit Validate Scene
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Action payload</div>
        <div className={cls("cardHint")}>The console should be a command deck, not a museum. These are the low-friction packets it can ship right now.</div>
        <pre className={cls("codeBox")}>
{JSON.stringify(
  {
    canonicalPath,
    sceneId: bindings.sceneStudio?.scene?.id ?? null,
    profile: diagnostics?.resolved.profile ?? runtime?.profile ?? null,
    enabledLayerIds: diagnostics?.enabledLayerIds ?? runtime?.enabledLayerIds ?? []
  },
  null,
  2
)}
        </pre>
      </section>
    </div>
  );
}
