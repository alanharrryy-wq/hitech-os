"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";
import { ALL_LAYERS } from "./layerIds.js";
import {
  createLayerFlagsQueryFromResolved,
  shouldRenderLayerDebugPanel
} from "./resolveLayerFlags.js";
import { useLayerFlags } from "./useLayerFlags.js";

export interface LayerDebugPanelProps {
  /**
   * "floating" lets a parent container handle position/size.
   * "fixed" keeps the legacy viewport-fixed panel.
   */
  mode?: "floating" | "fixed";
}

const FIXED_PANEL_STYLE: CSSProperties = {
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

const FLOATING_PANEL_STYLE: CSSProperties = {
  position: "relative",
  zIndex: 1,
  width: "100%",
  maxHeight: "unset",
  overflow: "visible",
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
  gap: "0.75rem",
  alignItems: "center",
  justifyContent: "space-between"
};

const BUTTON_STYLE: CSSProperties = {
  height: 32,
  padding: "0 0.75rem",
  borderRadius: 10,
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-2) / 0.9)",
  cursor: "pointer",
  fontSize: 12
};

const INPUT_STYLE: CSSProperties = {
  width: "100%",
  height: 32,
  padding: "0 0.65rem",
  borderRadius: 10,
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-0) / 0.85)",
  fontSize: 12
};

function createShareUrl(search: URLSearchParams): string {
  if (typeof window === "undefined") {
    return `?${search.toString()}`;
  }
  const query = search.toString();
  return `${window.location.origin}${window.location.pathname}${query ? `?${query}` : ""}`;
}

export function LayerDebugPanel({ mode = "fixed" }: LayerDebugPanelProps) {
  const { resolved, setFlag, setAll, setProfile, resetNeutral } = useLayerFlags();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const timeout = window.setTimeout(() => setCopied(false), 1200);
    return () => window.clearTimeout(timeout);
  }, [copied]);

  const shareUrl = useMemo(() => {
    if (typeof window === "undefined") return "";
    const next = createLayerFlagsQueryFromResolved(
      resolved,
      new URLSearchParams(window.location.search)
    );
    return createShareUrl(next);
  }, [resolved]);

  if (!shouldRenderLayerDebugPanel(resolved)) {
    return null;
  }

  const panelStyle = mode === "fixed" ? FIXED_PANEL_STYLE : FLOATING_PANEL_STYLE;

  return (
    <div style={panelStyle} aria-label="LayerDebugPanel">
      <div style={{ fontWeight: 700, fontSize: 13, opacity: 0.95 }}>Layer Debug</div>
      <div style={{ marginTop: 6, opacity: 0.75, fontSize: 12 }}>
        source={resolved.source} profile={resolved.profile} debug=1
      </div>

      <div style={SECTION_STYLE}>
        <div style={ROW_STYLE}>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("neutral")}>
            neutral
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("fx")}>
            fx
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setProfile("perf")}>
            perf
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={resetNeutral}>
            reset
          </button>
        </div>

        <div style={{ ...ROW_STYLE, marginTop: 8 }}>
          <button type="button" style={BUTTON_STYLE} onClick={() => setAll(true)}>
            layers=all
          </button>
          <button type="button" style={BUTTON_STYLE} onClick={() => setAll(false)}>
            layers=none
          </button>
          <button
            type="button"
            style={BUTTON_STYLE}
            onClick={() => {
              navigator.clipboard?.writeText(shareUrl).then(
                () => setCopied(true),
                () => setCopied(false)
              );
            }}
          >
            {copied ? "Copied" : "Copy URL"}
          </button>
        </div>

        <div style={{ marginTop: 10 }}>
          <input style={INPUT_STYLE} value={shareUrl} readOnly aria-label="Layer debug share URL" />
        </div>
      </div>

      <div style={SECTION_STYLE}>
        <div style={{ fontWeight: 650, fontSize: 12, opacity: 0.9, marginBottom: 8 }}>Layers</div>

        <div style={{ display: "grid", gap: 8 }}>
          {ALL_LAYERS.map((layerId) => {
            const enabled = Boolean(resolved.flags[layerId]);
            return (
              <label key={layerId} style={{ display: "flex", gap: 10, alignItems: "center" }}>
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(event) => setFlag(layerId, event.currentTarget.checked)}
                />
                <span style={{ fontSize: 12, opacity: 0.9 }}>{layerId}</span>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
}
