"use client";

import { useMemo, type CSSProperties, type PropsWithChildren } from "react";
import { LayerDebugPanel, LayerFlagsProvider, resolveLayerFlags, useLayerFlags } from "@hitech/ui-kit";
import { useSearchParams } from "next/navigation";
import { ControlRoomToolbarWindow } from "./ControlRoomToolbarWindow";
import { FloatingWindow } from "./FloatingWindow";
import { SceneGraphPanel } from "./SceneGraphPanel";
import { useOptionalDevConsole } from "../../../components/dev-console/DevConsoleContext";
import { InternalToolClientOnlyBoundary } from "../../../components/internal-tooling/internal-tool-client-only-boundary";
import {
  SceneStudioEditorPanel
} from "../../../components/dev-console/panels/SceneStudioEditorPanel";
import { useStudioHotkeys } from "./useStudioHotkeys";
import { SnapPreviewOverlay } from "./window-manager/SnapPreviewOverlay";
import { WindowManagerProvider } from "./window-manager/WindowManagerProvider";

const OVERLAY_ROOT_STYLE: CSSProperties = {
  position: "fixed",
  inset: 0,
  pointerEvents: "none",
  zIndex: 2147483600
};

const DEBUG_HINT_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.76rem",
  color: "hsl(var(--ui-text-3))"
};
const LEGACY_OVERLAY_PANEL_NAME = "SceneStudioLegacyControlRoomOverlay";

function StudioHotkeysBinding() {
  useStudioHotkeys();
  return null;
}

function LayerDebugWindowContent() {
  const { resolved } = useLayerFlags();

  if (!resolved.debug) {
    return <p style={DEBUG_HINT_STYLE}>Enable `?debug=1` to use Layer Debug controls.</p>;
  }

  return <LayerDebugPanel />;
}

function resolveFrameStyleFromQuery(
  requested: string | null
): "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO" {
  if (requested === "LIQUID_GLASS" || requested === "GOLD_NOIR_TERMINAL" || requested === "GRAPHITE_PRISM_ISO") {
    return requested;
  }

  return "GRAPHITE_PRISM_ISO";
}

export function ControlRoom({ children }: PropsWithChildren) {
  const devConsole = useOptionalDevConsole();
  const disableLegacyHud = Boolean(devConsole);
  const searchParams = useSearchParams();
  const searchSignature = searchParams.toString();
  const frameStyle = useMemo(
    () => resolveFrameStyleFromQuery(new URLSearchParams(searchSignature).get("luxStyle")),
    [searchSignature]
  );
  const framePerfProfile = useMemo<"quality" | "perf">(
    () => (new URLSearchParams(searchSignature).get("layerProfile") === "perf" ? "perf" : "quality"),
    [searchSignature]
  );

  const initialResolved = useMemo(() => {
    const params = Object.fromEntries(new URLSearchParams(searchSignature).entries());
    return resolveLayerFlags(params);
  }, [searchSignature]);

  return (
    <LayerFlagsProvider initialResolved={initialResolved}>
      <WindowManagerProvider>
        {children}

        {disableLegacyHud ? null : (
          <InternalToolClientOnlyBoundary componentName={LEGACY_OVERLAY_PANEL_NAME}>
            <div aria-label="Control Room overlay" style={OVERLAY_ROOT_STYLE}>
              <SnapPreviewOverlay />
              
                <ControlRoomToolbarWindow
                  frameStyle={frameStyle}
                  framePerfProfile={framePerfProfile}
                />

                <FloatingWindow
                  id="scene-editor"
                  title="Scene Editor"
                  defaultPos={{ x: 20, y: 112 }}
                  defaultSize={{ w: 500, h: 700 }}
                >
                  {devConsole?.bindings.sceneStudio ? (
                    <SceneStudioEditorPanel {...devConsole.bindings.sceneStudio} />
                  ) : (
                    <div>Scene Studio not available</div>
                  )}
                </FloatingWindow>

                <FloatingWindow
                  id="layer-debug"
                  title="Layer Debug"
                  defaultPos={{ x: 980, y: 20 }}
                  defaultSize={{ w: 400, h: 520 }}
                >
                  <LayerDebugWindowContent />
                </FloatingWindow>

                <FloatingWindow
                  id="scene-graph"
                  title="Scene Graph"
                  defaultPos={{ x: 980, y: 560 }}
                  defaultSize={{ w: 400, h: 300 }}
                >
                  <SceneGraphPanel />
                </FloatingWindow>
              
            </div>
          </InternalToolClientOnlyBoundary>
        )}

        <StudioHotkeysBinding />
      </WindowManagerProvider>
    </LayerFlagsProvider>
  );
}
