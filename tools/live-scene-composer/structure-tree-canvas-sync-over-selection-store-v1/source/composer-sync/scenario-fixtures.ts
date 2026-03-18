
import { type ObservedBoundsEntry, type SceneGraphInput, sceneRef, layoutNodeRef, slotRef, widgetRef } from "./contracts";

export function createMiniScene(): SceneGraphInput {
  return {
    sceneId: "scene-demo",
    sceneTitle: "Demo Scene",
    revision: "rev-001",
    rootLayoutNodeId: "layout-root",
    layoutNodes: {
      "layout-root": { id: "layout-root", kind: "root", title: "Root", childLayoutNodeIds: ["layout-grid-a", "layout-stack-b"], slotId: undefined },
      "layout-grid-a": { id: "layout-grid-a", kind: "grid", title: "Grid A", childLayoutNodeIds: [], slotId: "slot-kpi" },
      "layout-stack-b": { id: "layout-stack-b", kind: "stack", title: "Stack B", childLayoutNodeIds: ["layout-container-c"], slotId: "slot-copy" },
      "layout-container-c": { id: "layout-container-c", kind: "container", title: "Container C", childLayoutNodeIds: [], slotId: "slot-chart" }
    },
    slots: {
      "slot-kpi": { id: "slot-kpi", title: "KPI Slot", kind: "metric", widgetIds: ["widget-kpi-1"], acceptsMultiple: false },
      "slot-copy": { id: "slot-copy", title: "Copy Slot", kind: "content", widgetIds: ["widget-copy-1"], acceptsMultiple: true },
      "slot-chart": { id: "slot-chart", title: "Chart Slot", kind: "chart", widgetIds: ["widget-chart-1", "widget-chart-2"], acceptsMultiple: true }
    },
    widgets: {
      "widget-kpi-1": { id: "widget-kpi-1", title: "Revenue KPI", widgetType: "kpi", slotId: "slot-kpi", visible: true },
      "widget-copy-1": { id: "widget-copy-1", title: "Headline", widgetType: "text", slotId: "slot-copy", visible: true },
      "widget-chart-1": { id: "widget-chart-1", title: "Sales Chart", widgetType: "chart", slotId: "slot-chart", visible: true },
      "widget-chart-2": { id: "widget-chart-2", title: "Margin Chart", widgetType: "chart", slotId: "slot-chart", visible: false, locked: true }
    }
  };
}

export function createMiniBounds(): readonly ObservedBoundsEntry[] {
  return [
    { refKey: "scene:scene-demo", rect: { x: 0, y: 0, width: 1920, height: 1080 }, visible: true },
    { refKey: "layout-node:scene-demo:layout-grid-a", rect: { x: 20, y: 20, width: 700, height: 300 }, visible: true },
    { refKey: "layout-node:scene-demo:layout-stack-b", rect: { x: 760, y: 20, width: 500, height: 900 }, visible: true },
    { refKey: "slot:scene-demo:slot-kpi", rect: { x: 40, y: 40, width: 660, height: 260 }, visible: true },
    { refKey: "slot:scene-demo:slot-copy", rect: { x: 780, y: 40, width: 460, height: 200 }, visible: true },
    { refKey: "slot:scene-demo:slot-chart", rect: { x: 780, y: 280, width: 460, height: 620 }, visible: true },
    { refKey: "widget:scene-demo:widget-kpi-1", rect: { x: 60, y: 60, width: 620, height: 220 }, visible: true },
    { refKey: "widget:scene-demo:widget-copy-1", rect: { x: 800, y: 60, width: 420, height: 160 }, visible: true },
    { refKey: "widget:scene-demo:widget-chart-1", rect: { x: 800, y: 300, width: 420, height: 280 }, visible: true }
  ];
}

export const demoRefs = {
  scene: sceneRef("scene-demo"),
  grid: layoutNodeRef("scene-demo", "layout-grid-a"),
  slot: slotRef("scene-demo", "slot-chart"),
  widget: widgetRef("scene-demo", "widget-chart-1", "slot-chart")
};
