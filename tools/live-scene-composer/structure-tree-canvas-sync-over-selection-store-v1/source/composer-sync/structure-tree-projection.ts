
import { type EntityRef, type SceneGraphInput, type SelectionState, type StructureTreeNode, type StructureTreeProjection, layoutNodeRef, refKey, sceneRef, slotRef, widgetRef } from "./contracts";

function selectionBadge(selection: SelectionState, ref: EntityRef) {
  if (selection.status === "active" && selection.ref && refKey(selection.ref) === refKey(ref)) {
    return [{ kind: "selection" as const, label: "selected" }];
  }
  if (selection.status === "stale" && selection.ref && refKey(selection.ref) === refKey(ref)) {
    return [{ kind: "stale" as const, label: "stale" }];
  }
  return [];
}

export function buildStructureTreeProjection(input: SceneGraphInput, selection: SelectionState): StructureTreeProjection {
  const flatOrder: EntityRef[] = [];

  function visitLayoutNode(layoutNodeId: string): StructureTreeNode {
    const node = input.layoutNodes[layoutNodeId];
    const ref = layoutNodeRef(input.sceneId, layoutNodeId);
    flatOrder.push(ref);

    const childNodes = node.childLayoutNodeIds.map((childId) => visitLayoutNode(childId));
    const slotChildren = node.slotId ? [visitSlot(node.slotId)] : [];
    return {
      nodeId: `tree:${layoutNodeId}`,
      ref,
      kind: "layout-node",
      title: node.title,
      subtitle: node.kind,
      badges: [{ kind: "kind", label: node.kind }, ...selectionBadge(selection, ref)],
      expandedByDefault: node.kind === "root",
      children: [...slotChildren, ...childNodes]
    };
  }

  function visitSlot(slotId: string): StructureTreeNode {
    const slot = input.slots[slotId];
    const ref = slotRef(input.sceneId, slotId);
    flatOrder.push(ref);
    const children = slot.widgetIds.map((widgetId) => visitWidget(widgetId));
    return {
      nodeId: `tree:slot:${slotId}`,
      ref,
      kind: "slot",
      title: slot.title,
      subtitle: slot.kind,
      badges: [
        { kind: "kind", label: slot.kind },
        ...(slot.acceptsMultiple ? [{ kind: "kind" as const, label: "multi" }] : []),
        ...selectionBadge(selection, ref)
      ],
      expandedByDefault: true,
      children
    };
  }

  function visitWidget(widgetId: string): StructureTreeNode {
    const widget = input.widgets[widgetId];
    const ref = widgetRef(input.sceneId, widgetId, widget.slotId);
    flatOrder.push(ref);
    return {
      nodeId: `tree:widget:${widgetId}`,
      ref,
      kind: "widget",
      title: widget.title,
      subtitle: widget.widgetType,
      badges: [
        { kind: "kind", label: widget.widgetType },
        ...(widget.visible ? [] : [{ kind: "hidden" as const, label: "hidden" }]),
        ...(widget.locked ? [{ kind: "locked" as const, label: "locked" }] : []),
        ...selectionBadge(selection, ref)
      ],
      expandedByDefault: false,
      children: []
    };
  }

  const sceneNodeRef = sceneRef(input.sceneId);
  flatOrder.push(sceneNodeRef);
  const root: StructureTreeNode = {
    nodeId: `tree:scene:${input.sceneId}`,
    ref: sceneNodeRef,
    kind: "scene",
    title: input.sceneTitle,
    subtitle: "scene",
    badges: selectionBadge(selection, sceneNodeRef),
    expandedByDefault: true,
    children: [visitLayoutNode(input.rootLayoutNodeId)]
  };

  return { sceneId: input.sceneId, revision: input.revision, root, flatOrder };
}
