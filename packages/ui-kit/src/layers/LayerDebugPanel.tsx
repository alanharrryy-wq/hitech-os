"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";
import { ALL_LAYERS } from "./layerIds.js";
import { createShareableLayerUrl } from "./resolveLayerFlags.js";
import { useLayerFlags } from "./useLayerFlags.js";

const PANEL_STYLE: CSSProperties = {
  position: "fixed",
  right: "1rem",
  bottom: "1rem",
  zIndex: 2147483640,
  width: "min(460px, calc(100vw - 2rem))",
  maxHeight: "calc(100dvh - 2rem)",
  overflow: "auto",
  borderRadius: "12px",
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-1) / 0.96)",
  boxShadow: "var(--ui-shadow-2)",
  padding: "0.875rem"
};

const SECTION_STYLE: CSSProperties = {
  marginTop: "0.75rem",
  borderTop: "1px solid hsl(var(--ui-border-1))",
  paddingTop: "0.75rem"
};

const ROW_STYLE: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "0.5rem",
  paddingBlock: "0.225rem"
};

const BUTTON_ROW_STYLE: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: "0.4rem"
};

const BUTTON_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-2))",
  color: "hsl(var(--ui-text-1))",
  borderRadius: "0.5rem",
  fontSize: "0.78rem",
  padding: "0.35rem 0.6rem",
  cursor: "pointer"
};

const SMALL_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.72rem",
  color: "hsl(var(--ui-text-3))"
};

const WARNING_STYLE: CSSProperties = {
  margin: "0.35rem 0 0",
  fontSize: "0.72rem",
  color: "hsl(25 86% 45%)"
};

const LAYER_TOGGLE_IDS = ALL_LAYERS.filter((id) => id !== "motion.enabled");

function getCurrentShareUrl(
  resolved: ReturnType<typeof useLayerFlags>["resolved"]
): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return createShareableLayerUrl(resolved, {
    origin: window.location.origin,
    pathname: window.location.pathname,
    search: window.location.search
  });
}

export function LayerDebugPanel() {
  const { resolved, enabledLayers, setLayer, setAll, setProfile, setMotion, resetNeutral } =
    useLayerFlags();
  const [copyStatus, setCopyStatus] = useState<string>("idle");

  const shareUrl = useMemo(() => getCurrentShareUrl(resolved), [resolved]);

  if (process.env["NODE_ENV"] === "production" || !resolved.debug) {
    return null;
  }

  const handleCopyShareUrl = async () => {
    if (!shareUrl || typeof navigator === "undefined" || !navigator.clipboard) {
      setCopyStatus("copy-unavailable");
      return;
    }

    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopyStatus("copied");
      window.setTimeout(() => setCopyStatus("idle"), 1300);
    } catch {
      setCopyStatus("copy-unavailable");
    }
  };

  const handleExportSnapshot = () => {
    if (typeof window === "undefined") {
      return;
    }

    const snapshot = {
      route: window.location.pathname,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      resolved: {
        source: resolved.source,
        baseSource: resolved.baseSource,
        motionSource: resolved.motionSource,
        profile: resolved.profile,
        debug: resolved.debug,
        flags: resolved.flags,
        unknownTokens: resolved.unknownTokens
      },
      url: shareUrl
    };

    const blob = new Blob([JSON.stringify(snapshot, null, 2)], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const now = new Date().toISOString().replaceAll(":", "-");

    anchor.href = url;
    anchor.download = `layer-diagnostic-${now}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <aside style={PANEL_STYLE} aria-label="Layer Debug Panel">
      <header>
        <h2 style={{ margin: 0, fontSize: "0.96rem", lineHeight: 1.1 }}>Layer Flags Debug</h2>
        <p style={SMALL_STYLE}>
          source={resolved.source} profile={resolved.profile} motion={resolved.flags["motion.enabled"] ? "on" : "off"}
        </p>
        <p style={SMALL_STYLE}>
          enabled={enabledLayers.length} base={resolved.baseSource} motionSource={resolved.motionSource}
        </p>
        {resolved.unknownTokens.length > 0 ? (
          <p style={WARNING_STYLE}>Unknown layer tokens ignored: {resolved.unknownTokens.join(", ")}</p>
        ) : null}
      </header>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Profile Mode</p>
        <div style={BUTTON_ROW_STYLE}>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("neutral")}>
            layerProfile=neutral
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("fx")}>
            layerProfile=fx
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("perf")}>
            layerProfile=perf
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={resetNeutral}>
            defaults
          </button>
        </div>
      </section>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Explicit Layers Mode</p>
        <div style={BUTTON_ROW_STYLE}>
          <button type="button" style={BUTTON_STYLE} onClick={() => setAll(true)}>
            layers=all
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setAll(false)}>
            layers=none
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setMotion(true)}>
            motion=on
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setMotion(false)}>
            motion=off
          </button>
        </div>
      </section>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Share & Diagnostics</p>
        <div style={BUTTON_ROW_STYLE}>
          <button type="button" style={BUTTON_STYLE} onClick={handleCopyShareUrl}>
            {copyStatus === "copied" ? "Copied" : "Copy Scene Link"}
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={handleExportSnapshot}>
            Export Diagnostic
          </button>
        </div>
        {copyStatus === "copy-unavailable" ? (
          <p style={WARNING_STYLE}>Clipboard unavailable in this runtime.</p>
        ) : null}
        {shareUrl ? <p style={SMALL_STYLE}>{shareUrl}</p> : null}
      </section>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Layer Flags</p>
        {LAYER_TOGGLE_IDS.map((id) => {
          const checked = resolved.flags[id];
          return (
            <label key={id} style={ROW_STYLE}>
              <span style={{ fontSize: "0.76rem" }}>{id}</span>
              <input
                type="checkbox"
                checked={checked}
                onChange={(event) => {
                  setLayer(id, event.currentTarget.checked);
                }}
              />
            </label>
          );
        })}
      </section>
    </aside>
  );
}
