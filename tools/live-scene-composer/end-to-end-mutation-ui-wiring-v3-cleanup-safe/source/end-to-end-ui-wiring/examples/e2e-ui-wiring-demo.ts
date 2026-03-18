import { buildSelectionContext } from "../selection-context";
import { createInspectorWidgetStyleAction } from "../inspector-surface";
import { SurfaceCoordinator } from "../surface-coordinator";

async function demo() {
  const context = buildSelectionContext({
    selection: { kind: "widget", sceneId: "scene-home", slotId: "slot-hero", widgetId: "widget-title", selectionId: "sel-widget-title" },
    draftRevision: "draft-r42",
    baselineRevision: "base-r41",
    activeMode: "safe"
  });

  const coordinator = new SurfaceCoordinator(context);
  const action = createInspectorWidgetStyleAction(context, { fontSize: 42, color: "#ffffff" });
  const result = await coordinator.dispatch(action);
  return { state: coordinator.readState(), result };
}

void demo();
