import { useLiveSceneComposer } from "../LiveSceneComposerProvider";
import { getCompatiblePrefabs } from "../prefabs/prefab-catalog";

export function InspectorPanel(): any {
  const composer = useLiveSceneComposer();
  const { inspectorTarget, state } = composer;
  const preview = state.documents.preview;
  const target = state.selection.primaryTarget;

  const layoutTarget = target && target.kind === "layout-node" ? target : null;
  const slotTarget = target && target.kind === "slot" ? target : null;
  const widgetTarget = target && target.kind === "widget" ? target : null;
  const slotEntity = slotTarget ? preview.slots[slotTarget.id] : undefined;

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <header>
        <h3>Inspector</h3>
        <small>{inspectorTarget.title}</small>
      </header>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, border: "1px solid rgba(148,163,184,0.25)", borderRadius: 16, padding: 12 }}>
        <p>{inspectorTarget.description}</p>

        {inspectorTarget.surface === "scene-look" ? (
          <>
            <strong>Scene Look</strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {(["neutral", "gradient", "cinematic"] as const).map((value) => (
                <button key={value} onClick={() => composer.previewSceneLook({ background: value })}>
                  {value}
                </button>
              ))}
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <button onClick={() => composer.previewSceneLook({ overlays: { grid: !preview.scene.look.overlays.grid } })}>
                toggle grid
              </button>
              <button onClick={() => composer.previewSceneLook({ overlays: { safeAreas: !preview.scene.look.overlays.safeAreas } })}>
                toggle safe areas
              </button>
              <button onClick={() => composer.previewSceneLook({ visualEffects: { bloom: !preview.scene.look.visualEffects.bloom } })}>
                toggle bloom
              </button>
              <button onClick={() => composer.previewSceneLook({ stageStyle: preview.scene.look.stageStyle === "default" ? "cinematic" : "default" })}>
                stage style
              </button>
              <button onClick={() => composer.previewSceneLook({ cardStyle: preview.scene.look.cardStyle === "glass" ? "default" : "glass" })}>
                card style
              </button>
              <button onClick={() => composer.previewSceneLook({ motion: preview.scene.look.motion === "on" ? "reduced" : "on" })}>
                motion
              </button>
              <button onClick={() => composer.previewSceneLook({ density: preview.scene.look.density === "compact" ? "comfortable" : "compact" })}>
                density
              </button>
            </div>
          </>
        ) : null}

        {inspectorTarget.surface === "layout-node" && layoutTarget ? (
          <>
            <strong>Layout Node</strong>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <button onClick={() => composer.moveLayoutNode(layoutTarget, -12, 0)}>left</button>
              <button onClick={() => composer.moveLayoutNode(layoutTarget, 12, 0)}>right</button>
              <button onClick={() => composer.moveLayoutNode(layoutTarget, 0, -12)}>up</button>
              <button onClick={() => composer.moveLayoutNode(layoutTarget, 0, 12)}>down</button>
              <button onClick={() => composer.resizeLayoutNode(layoutTarget, 18, 0)}>wider</button>
              <button onClick={() => composer.resizeLayoutNode(layoutTarget, 0, 18)}>taller</button>
            </div>
          </>
        ) : null}

        {inspectorTarget.surface === "slot" && slotTarget && slotEntity ? (
          <>
            <strong>Compatible Prefabs</strong>
            {getCompatiblePrefabs(slotEntity).map((prefab) => (
              <button key={prefab.id} onClick={() => composer.insertWidgetFromPrefab(slotTarget, prefab)}>
                {prefab.title}
              </button>
            ))}
          </>
        ) : null}

        {inspectorTarget.surface === "widget" && widgetTarget ? (
          <>
            <strong>Widget Controls</strong>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <button onClick={() => composer.updateWidgetProps(widgetTarget, { title: "Edited Widget" })}>preview title</button>
              <button onClick={() => composer.updateWidgetProps(widgetTarget, { text: "Edited in inspector" })}>preview content</button>
              <button onClick={() => composer.updateWidgetStyle(widgetTarget, { borderStyle: "glass" })}>glass</button>
              <button onClick={() => composer.updateWidgetStyle(widgetTarget, { borderStyle: "solid" })}>solid</button>
              <button onClick={() => composer.updateWidgetStyle(widgetTarget, { emphasis: "strong" })}>emphasis</button>
              <button onClick={() => composer.removeWidget(widgetTarget)}>remove</button>
            </div>
          </>
        ) : null}

        {target ? <button onClick={() => composer.resetSelectedElement()}>reset selected</button> : null}
        <small>Relevant controls only. Inspector Target is derived from Selection and does not compete with it.</small>
      </div>
    </section>
  );
}
