import type {
  AuthoringWorkbenchState,
  CanvasBox,
  LayoutNode,
  LayoutNodeId,
  PrefabDefinition,
  SceneDocument,
  SelectionTarget,
  SlotEntity,
  StructureTreeEntry,
  WidgetEntity,
  WidgetStyle,
} from "../authoring-workbench-contracts";

export function cloneSceneDocument(document: SceneDocument): SceneDocument {
  return JSON.parse(JSON.stringify(document)) as SceneDocument;
}

export function isDraftDirty(state: AuthoringWorkbenchState): boolean {
  return JSON.stringify(state.documents.baseline) !== JSON.stringify(state.documents.draft);
}

export function getLayoutNode(document: SceneDocument, layoutNodeId: LayoutNodeId): LayoutNode | null {
  return document.layoutNodes[layoutNodeId] ?? null;
}

export function getSlot(document: SceneDocument, slotId: string): SlotEntity | null {
  return document.slots[slotId] ?? null;
}

export function getWidget(document: SceneDocument, widgetId: string): WidgetEntity | null {
  return document.widgets[widgetId] ?? null;
}

export function getWidgetsForSlot(document: SceneDocument, slotId: string): readonly WidgetEntity[] {
  const slot = document.slots[slotId];
  if (!slot) {
    return [];
  }
  return slot.widgetIds.map((widgetId) => document.widgets[widgetId]).filter((widget): widget is WidgetEntity => Boolean(widget));
}

export function createWidgetFromPrefab(prefab: PrefabDefinition, slotId: string, nextId: number): WidgetEntity {
  const widgetId = `widget-${nextId}`;
  return {
    id: widgetId,
    title: prefab.title,
    type: prefab.widgetType,
    slotId,
    prefabId: prefab.id,
    capabilities: prefab.acceptedCapabilities,
    props: prefab.defaultProps,
    style: prefab.defaultStyle,
    visible: true,
    locked: false,
  };
}

export function listStructureEntries(document: SceneDocument): readonly StructureTreeEntry[] {
  const entries: StructureTreeEntry[] = [];
  const visitLayout = (layoutNodeId: string, depth: number, parentId: string | null): void => {
    const layoutNode = document.layoutNodes[layoutNodeId];
    if (!layoutNode) {
      return;
    }
    entries.push({
      id: layoutNode.id,
      kind: "layout-node",
      title: layoutNode.title,
      depth,
      parentId,
      selectionTarget: { kind: "layout-node", id: layoutNode.id, sceneId: document.scene.id },
      childIds: [...layoutNode.childIds, ...(layoutNode.slotId ? [layoutNode.slotId] : [])],
    });
    if (layoutNode.slotId) {
      const slot = document.slots[layoutNode.slotId];
      if (slot) {
        entries.push({
          id: slot.id,
          kind: "slot",
          title: slot.title,
          depth: depth + 1,
          parentId: layoutNode.id,
          selectionTarget: { kind: "slot", id: slot.id, sceneId: document.scene.id },
          childIds: [...slot.widgetIds],
        });
        for (const widgetId of slot.widgetIds) {
          const widget = document.widgets[widgetId];
          if (!widget) {
            continue;
          }
          entries.push({
            id: widget.id,
            kind: "widget",
            title: widget.title,
            depth: depth + 2,
            parentId: slot.id,
            selectionTarget: { kind: "widget", id: widget.id, sceneId: document.scene.id },
            childIds: [],
          });
        }
      }
    }
    for (const childId of layoutNode.childIds) {
      visitLayout(childId, depth + 1, layoutNode.id);
    }
  };

  entries.push({
    id: document.scene.id,
    kind: "scene",
    title: document.scene.title,
    depth: 0,
    parentId: null,
    selectionTarget: { kind: "scene", id: document.scene.id, sceneId: document.scene.id },
    childIds: [document.rootLayoutId],
  });
  visitLayout(document.rootLayoutId, 1, document.scene.id);
  return entries;
}

export function getSelectionLabel(document: SceneDocument, selection: SelectionTarget | null): string {
  if (!selection) {
    return "Nothing selected";
  }
  if (selection.kind === "scene") {
    return `Scene: ${document.scene.title}`;
  }
  if (selection.kind === "layout-node") {
    return `Layout: ${document.layoutNodes[selection.id]?.title ?? selection.id}`;
  }
  if (selection.kind === "slot") {
    return `Slot: ${document.slots[selection.id]?.title ?? selection.id}`;
  }
  return `Widget: ${document.widgets[selection.id]?.title ?? selection.id}`;
}

export function buildCanvasBoxes(document: SceneDocument, selectedTarget: SelectionTarget | null): readonly CanvasBox[] {
  const boxes: CanvasBox[] = [];
  for (const layoutNode of Object.values(document.layoutNodes)) {
    boxes.push({
      id: layoutNode.id,
      kind: "layout-node",
      title: layoutNode.title,
      frame: layoutNode.frame,
      selected: selectedTarget?.kind === "layout-node" && selectedTarget.id === layoutNode.id,
      slotId: layoutNode.slotId,
      widgetIds: layoutNode.slotId ? [...(document.slots[layoutNode.slotId]?.widgetIds ?? [])] : [],
    });
    if (layoutNode.slotId) {
      const slot = document.slots[layoutNode.slotId];
      if (!slot) {
        continue;
      }
      boxes.push({
        id: slot.id,
        kind: "slot",
        title: slot.title,
        frame: layoutNode.frame,
        selected: selectedTarget?.kind === "slot" && selectedTarget.id === slot.id,
        slotId: slot.id,
        widgetIds: [...slot.widgetIds],
      });
      const widgets = getWidgetsForSlot(document, slot.id);
      widgets.forEach((widget, index) => {
        boxes.push({
          id: widget.id,
          kind: "widget",
          title: widget.title,
          frame: {
            x: layoutNode.frame.x + 8,
            y: layoutNode.frame.y + 8 + index * 56,
            width: Math.max(layoutNode.frame.width - 16, 40),
            height: 48,
          },
          selected: selectedTarget?.kind === "widget" && selectedTarget.id === widget.id,
          slotId: slot.id,
          widgetIds: [widget.id],
        });
      });
    }
  }
  return boxes;
}

export function coerceStylePatch(previous: WidgetStyle, patch: Partial<WidgetStyle>): WidgetStyle {
  return {
    background: patch.background ?? previous.background,
    foreground: patch.foreground ?? previous.foreground,
    borderStyle: patch.borderStyle ?? previous.borderStyle,
    radius: typeof patch.radius === "number" ? patch.radius : previous.radius,
    emphasis: patch.emphasis ?? previous.emphasis,
  };
}
