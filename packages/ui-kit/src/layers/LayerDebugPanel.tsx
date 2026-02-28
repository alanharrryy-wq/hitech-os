"use client";

import type { CSSProperties } from "react";
import { ALL_LAYERS } from "./layerIds.js";
import { useLayerFlags } from "./useLayerFlags.js";

const PANEL_STYLE: CSSProperties = {
  position: "fixed",
  right: "1rem",
  bottom: "1rem",
  zIndex: 2147483640,
  width: "min(420px, calc(100vw - 2rem))",
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

export function LayerDebugPanel() {
  const { resolved, enabledLayers, setLayer, setAll, setProfile, resetNeutral } = useLayerFlags();
  if (process.env["NODE_ENV"] === "production" || !resolved.debug) {
    return null;
  }

  return (
    <aside style={PANEL_STYLE} aria-label="Layer Debug Panel">
      <header>
        <h2 style={{ margin: 0, fontSize: "0.96rem", lineHeight: 1.1 }}>Layer Toggle Debugging</h2>
        <p style={SMALL_STYLE}>
          source={resolved.source} profile={resolved.profile} debug=1
        </p>
        <p style={SMALL_STYLE}>enabled={enabledLayers.length}</p>
      </header>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Profile Mode</p>
        <div style={BUTTON_ROW_STYLE}>
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
            resetNeutral
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
        </div>
      </section>

      <section style={SECTION_STYLE}>
        <p style={{ margin: 0, fontSize: "0.78rem", fontWeight: 600 }}>Layer Flags</p>
        {ALL_LAYERS.map((id) => {
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
