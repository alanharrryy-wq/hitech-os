"use client";

import { useMemo, type CSSProperties, type PropsWithChildren } from "react";
import { LayerDebugPanel, LayerFlagsProvider, resolveLayerFlags, useLayerFlags } from "@hitech/ui-kit";
import { useSearchParams } from "next/navigation";
import { ControlRoomToolbarWindow } from "./ControlRoomToolbarWindow";
import { FloatingWindow } from "./FloatingWindow";
import { SceneGraphPanel } from "./SceneGraphPanel";
import {
  SceneStudioEditorPanel,
  SceneStudioRuntimeProvider
} from "./SceneStudioEditor";
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

function StudioHotkeysBinding() {
  useStudioHotkeys();
  return null;
}

function LayerDebugWindowContent() {
  const { resolved } = useLayerFlags();

  if (!resolved.debug) {
    return <p style={DEBUG_HINT_STYLE}>Enable `?debug=1` to use Layer Debug controls.</p>;
  }

  return <LayerDebugPanel inline />;
}

export function ControlRoom({ children }: PropsWithChildren) {
  const searchParams = useSearchParams();
  const searchSignature = searchParams.toString();

  const initialResolved = useMemo(() => {
    const params = Object.fromEntries(new URLSearchParams(searchSignature).entries());
    return resolveLayerFlags(params);
  }, [searchSignature]);

  return (
    <LayerFlagsProvider initialResolved={initialResolved}>
      <WindowManagerProvider>
        {children}

        <div aria-label="Control Room overlay" style={OVERLAY_ROOT_STYLE}>
          <SnapPreviewOverlay />
          <SceneStudioRuntimeProvider>
            <ControlRoomToolbarWindow />

            <FloatingWindow
              id="scene-editor"
              title="Scene Editor"
              minWidth={360}
              minHeight={320}
              defaultState={{
                x: 20,
                y: 112,
                w: 500,
                h: 700,
                z: 1101,
                visible: true,
                collapsed: false
              }}
            >
              <SceneStudioEditorPanel />
            </FloatingWindow>

            <FloatingWindow
              id="layer-debug"
              title="Layer Debug"
              minWidth={340}
              minHeight={240}
              defaultState={{
                x: 980,
                y: 20,
                w: 400,
                h: 520,
                z: 1102,
                visible: true,
                collapsed: false
              }}
            >
              <LayerDebugWindowContent />
            </FloatingWindow>

            <FloatingWindow
              id="scene-graph"
              title="Scene Graph"
              minWidth={340}
              minHeight={220}
              defaultState={{
                x: 980,
                y: 560,
                w: 400,
                h: 300,
                z: 1103,
                visible: true,
                collapsed: false
              }}
            >
              <SceneGraphPanel />
            </FloatingWindow>
          </SceneStudioRuntimeProvider>
        </div>

        <StudioHotkeysBinding />
      </WindowManagerProvider>
    </LayerFlagsProvider>
  );
}
