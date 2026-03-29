"use client";

import { useMemo, useState } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

async function copyText(text: string): Promise<boolean> {
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  if (typeof document === "undefined") {
    return false;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  return copied;
}

export function PitchShareLookPanel() {
  const { diagnostics, runtime, bindings } = useDevConsole();
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");

  const canonicalPath = useMemo(() => {
    const route = diagnostics?.route ?? runtime?.route ?? "/pitch";
    const query = diagnostics?.query ?? runtime?.query ?? "";
    return `${route}${query}`;
  }, [diagnostics?.query, diagnostics?.route, runtime?.query, runtime?.route]);

  const sharePayload = useMemo(
    () => ({
      canonicalPath,
      sceneId: bindings.sceneStudio?.scene?.id ?? null,
      sceneTitle: bindings.sceneStudio?.scene?.title ?? null,
      profile: diagnostics?.resolved.profile ?? runtime?.profile ?? null,
      source: diagnostics?.resolved.source ?? runtime?.source ?? null,
      enabledLayerIds: diagnostics?.enabledLayerIds ?? runtime?.enabledLayerIds ?? [],
      missingDataAttributes: diagnostics?.missingDataAttributes ?? [],
      timestamp: diagnostics?.timestamp ?? runtime?.timestamp ?? null
    }),
    [
      bindings.sceneStudio?.scene?.id,
      bindings.sceneStudio?.scene?.title,
      canonicalPath,
      diagnostics?.enabledLayerIds,
      diagnostics?.missingDataAttributes,
      diagnostics?.resolved.profile,
      diagnostics?.resolved.source,
      diagnostics?.timestamp,
      runtime?.enabledLayerIds,
      runtime?.profile,
      runtime?.source,
      runtime?.timestamp
    ]
  );

  const handleCopy = async (value: string) => {
    const ok = await copyText(value);
    setCopyState(ok ? "copied" : "failed");
    window.setTimeout(() => setCopyState("idle"), 1200);
  };

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Share-ready route</div>
        <div className={cls("cardHint")}>
          This panel turns the current scene and diagnostics state into a clean artifact you can paste into chat,
          tickets, or visual review threads.
        </div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Canonical path</div>
            <div className={cls("kvValue")}>{canonicalPath}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Scene</div>
            <div className={cls("kvValue")}>{bindings.sceneStudio?.scene?.title ?? "unbound"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Profile</div>
            <div className={cls("kvValue")}>{sharePayload.profile ?? "pending"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Enabled layers</div>
            <div className={cls("kvValue")}>{sharePayload.enabledLayerIds.length}</div>
          </div>
        </div>

        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={() => void handleCopy(canonicalPath)}>
            {copyState === "copied" ? "Copied" : "Copy Path"}
          </button>
          <button
            type="button"
            className={cls("button")}
            onClick={() => void handleCopy(JSON.stringify(sharePayload, null, 2))}
          >
            Copy JSON
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Share payload</div>
        <div className={cls("cardHint")}>Tight payload, low drama. Enough context to reproduce the scene without dragging the whole studio along.</div>
        <pre className={cls("codeBox")}>{JSON.stringify(sharePayload, null, 2)}</pre>
      </section>
    </div>
  );
}
