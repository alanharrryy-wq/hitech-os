import { useMemo, type MouseEvent, type ReactElement } from "react";
import { useLiveSceneComposer } from "../LiveSceneComposerProvider";
import { createCanvasOverlayModel } from "./canvas-view-model";

const gridLineStyle = { position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.16 } as const;

export function CanvasSurface(): ReactElement {
  const composer = useLiveSceneComposer();
  const { state, inspectorTarget } = composer;
  const overlay = useMemo(
    () => createCanvasOverlayModel(state.documents.preview, state.selection.primaryTarget, inspectorTarget, state.runtimeObserved),
    [state.documents.preview, state.selection.primaryTarget, inspectorTarget, state.runtimeObserved]
  );
  const sceneLook = state.documents.preview.scene.look;
  const background =
    sceneLook.background === "cinematic"
      ? "linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #020617 100%)"
      : sceneLook.background === "gradient"
      ? "linear-gradient(135deg, #172554 0%, #1d4ed8 45%, #0ea5e9 100%)"
      : "linear-gradient(180deg, #111827 0%, #1f2937 100%)";
  const transition = sceneLook.motion === "off" ? "none" : sceneLook.motion === "reduced" ? "all 120ms ease-out" : "all 220ms ease-out";
  const densityPadding = sceneLook.density === "compact" ? 6 : 12;
  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <header>
        <h3>Canvas</h3>
        <small>{overlay.inspectorHint}</small>
      </header>
      <div
        style={{
          position: "relative",
          minHeight: 640,
          borderRadius: 20,
          overflow: "hidden",
          border: sceneLook.cardStyle === "glass" ? "1px solid rgba(255,255,255,0.22)" : "1px solid rgba(148,163,184,0.35)",
          background,
          padding: densityPadding,
          transition,
        }}
      >
        {overlay.showGrid ? (
          <div style={gridLineStyle}>
            {Array.from({ length: 12 }).map((_, index) => (
              <div key={`grid-x-${index}`} style={{ position: "absolute", top: 0, bottom: 0, left: `${index * 8.33}%`, width: 1, background: "rgba(255,255,255,0.08)" }} />
            ))}
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={`grid-y-${index}`} style={{ position: "absolute", left: 0, right: 0, top: `${index * 12.5}%`, height: 1, background: "rgba(255,255,255,0.08)" }} />
            ))}
          </div>
        ) : null}
        {overlay.showSafeAreas ? (
          <div style={{ position: "absolute", inset: 18, border: "1px dashed rgba(248,250,252,0.45)", borderRadius: 14, pointerEvents: "none" }} />
        ) : null}
        {overlay.boxes.map((box) => {
          const borderColor = box.selected ? "#38bdf8" : box.kind === "slot" ? "rgba(255,255,255,0.26)" : "rgba(226,232,240,0.16)";
          const fill = box.kind === "widget" ? "rgba(255,255,255,0.10)" : box.kind === "slot" ? "rgba(255,255,255,0.05)" : "rgba(15,23,42,0.16)";
          return (
            <div
              key={`${box.kind}-${box.id}`}
              onClick={() => composer.select({ kind: box.kind, id: box.id, sceneId: state.documents.preview.scene.id }, "canvas")}
              style={{
                position: "absolute",
                left: box.frame.x,
                top: box.frame.y,
                width: box.frame.width,
                height: box.frame.height,
                borderRadius: 16,
                border: `1px solid ${borderColor}`,
                background: fill,
                boxShadow: box.selected ? "0 0 0 2px rgba(56,189,248,0.35) inset" : "none",
                padding: 10,
                color: "#f8fafc",
                cursor: "pointer",
                transition,
              }}
            >
              <strong>{box.title}</strong>
              <div style={{ fontSize: 12, opacity: 0.75 }}>{box.kind}</div>
              {box.kind === "widget" ? <div style={{ marginTop: 10, fontSize: 12 }}>Preview-aware widget chrome</div> : null}
              {box.selected && box.kind === "layout-node" ? (
                <div style={{ position: "absolute", right: 8, top: 8, display: "flex", gap: 4, flexWrap: "wrap", width: 120, justifyContent: "flex-end" }}>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.moveLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, 0, -8); }}>↑</button>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.moveLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, -8, 0); }}>←</button>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.moveLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, 8, 0); }}>→</button>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.moveLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, 0, 8); }}>↓</button>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.resizeLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, 16, 0); }}>W+</button>
                  <button onClick={(event: MouseEvent<HTMLButtonElement>) => { event.stopPropagation(); composer.resizeLayoutNode({ kind: "layout-node", id: box.id, sceneId: state.documents.preview.scene.id }, 0, 16); }}>H+</button>
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
