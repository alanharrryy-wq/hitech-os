"use client";

import { useMemo, type CSSProperties } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useLayerFlags } from "@hitech/ui-kit";

const PANEL_STYLE: CSSProperties = {
  display: "grid",
  gap: 10,
  fontSize: 12
};

const ROW_STYLE: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 8
};

const KICKER_STYLE: CSSProperties = {
  fontSize: 11,
  opacity: 0.75
};

const CHIP_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-2))",
  borderRadius: 8,
  padding: "2px 8px",
  background: "hsl(var(--ui-surface-2) / 0.8)"
};

export function PitchVisualSceneOverlay() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const layerState = useLayerFlags();
  const resolved = layerState.resolved ?? layerState;

  const enabledLayers = useMemo(
    () =>
      Object.entries(resolved.flags)
        .filter(([, enabled]) => enabled)
        .map(([id]) => id),
    [resolved.flags]
  );

  return (
    <div style={PANEL_STYLE} aria-label="PitchVisualSceneOverlay">
      <div style={ROW_STYLE}>
        <span style={KICKER_STYLE}>Path</span>
        <span>{pathname}</span>
      </div>

      <div style={ROW_STYLE}>
        <span style={KICKER_STYLE}>Query</span>
        <span>{searchParams.toString() || "(none)"}</span>
      </div>

      <div style={{ display: "grid", gap: 6 }}>
        <span style={KICKER_STYLE}>Enabled layers ({enabledLayers.length})</span>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {enabledLayers.length === 0 ? <span style={KICKER_STYLE}>No active layers</span> : null}
          {enabledLayers.map((layerId) => (
            <span key={layerId} style={CHIP_STYLE}>
              {layerId}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
