"use client";

import { useMemo, type CSSProperties } from "react";
import { usePathname } from "next/navigation";
import { useLayerFlags } from "@hitech/ui-kit";
import { KNOWN_PITCH_ROUTES } from "../../../lib/scene-studio";
import { useOptionalDevConsole } from "../../../components/dev-console/DevConsoleContext";
import { useWindowManager } from "./window-manager/useWindowManager";

const ROOT_STYLE: CSSProperties = {
  display: "grid",
  gap: "0.65rem",
  fontSize: "0.76rem"
};

const SECTION_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-1))",
  borderRadius: "10px",
  padding: "0.55rem",
  background: "color-mix(in oklab, hsl(var(--ui-surface-2)) 65%, transparent)"
};

const TITLE_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.72rem",
  letterSpacing: "0.05em",
  textTransform: "uppercase"
};

const LIST_STYLE: CSSProperties = {
  margin: "0.4rem 0 0",
  paddingLeft: "1rem",
  display: "grid",
  gap: "0.24rem"
};

const WARNING_STYLE: CSSProperties = {
  margin: 0,
  color: "hsl(20 82% 48%)",
  fontSize: "0.74rem"
};

export function SceneGraphPanel() {
  const pathname = usePathname();
  const { resolved, enabledLayers } = useLayerFlags();
  const { state, duplicateWindowIds } = useWindowManager();
  const devConsole = useOptionalDevConsole();
  const currentScene = devConsole?.bindings.sceneStudio?.scene;

  const activeRoute = currentScene?.route ?? pathname;

  const warnings = useMemo(() => {
    const nextWarnings: string[] = [];

    if (duplicateWindowIds.length > 0) {
      nextWarnings.push(`Duplicate window mounts detected: ${duplicateWindowIds.join(", ")}`);
    }

    if (activeRoute && !KNOWN_PITCH_ROUTES.includes(activeRoute as (typeof KNOWN_PITCH_ROUTES)[number])) {
      nextWarnings.push(`Unknown route not in known list: ${activeRoute}`);
    }

    if (currentScene?.layers.mode === "list" && currentScene.layers.layerIds.length === 0) {
      nextWarnings.push("Scene is in layers=list mode but no layers are enabled.");
    }

    return nextWarnings;
  }, [activeRoute, currentScene?.layers.layerIds.length, currentScene?.layers.mode, duplicateWindowIds]);

  const registeredWindows = useMemo(
    () => Object.keys(state.registrations).sort((left, right) => left.localeCompare(right)),
    [state.registrations]
  );

  const visibleWindows = useMemo(
    () =>
      Object.entries(state.windows)
        .filter(([, entry]) => entry.visible)
        .map(([windowId]) => windowId)
        .sort((left, right) => left.localeCompare(right)),
    [state.windows]
  );

  return (
    <div style={ROOT_STYLE}>
      <section style={SECTION_STYLE}>
        <p style={TITLE_STYLE}>Scene</p>
        <ul style={LIST_STYLE}>
          <li>Route: {activeRoute}</li>
          <li>
            Active Scene: {currentScene ? `${currentScene.id} (${currentScene.title})` : "none"}
          </li>
          <li>Motion (scene): {currentScene?.motion ?? "n/a"}</li>
          <li>Motion flag (runtime): {resolved.flags["motion.enabled"] ? "on" : "off"}</li>
        </ul>
      </section>

      <section style={SECTION_STYLE}>
        <p style={TITLE_STYLE}>Layers</p>
        <ul style={LIST_STYLE}>
          <li>Resolved source: {resolved.source}</li>
          <li>Mode: {currentScene?.layers.mode ?? "n/a"}</li>
          <li>Enabled count: {enabledLayers.length}</li>
          {enabledLayers.map((layerId) => (
            <li key={layerId}>{layerId}</li>
          ))}
        </ul>
      </section>

      <section style={SECTION_STYLE}>
        <p style={TITLE_STYLE}>Windows</p>
        <ul style={LIST_STYLE}>
          <li>Registered ({registeredWindows.length})</li>
          {registeredWindows.map((windowId) => (
            <li key={`registered-${windowId}`}>{windowId}</li>
          ))}
        </ul>
        <ul style={LIST_STYLE}>
          <li>Visible ({visibleWindows.length})</li>
          {visibleWindows.map((windowId) => (
            <li key={`visible-${windowId}`}>{windowId}</li>
          ))}
        </ul>
      </section>

      <section style={SECTION_STYLE}>
        <p style={TITLE_STYLE}>Warnings</p>
        {warnings.length === 0 ? <p style={{ margin: "0.4rem 0 0" }}>No warnings.</p> : null}
        {warnings.map((warning) => (
          <p key={warning} style={WARNING_STYLE}>
            {warning}
          </p>
        ))}
      </section>
    </div>
  );
}
