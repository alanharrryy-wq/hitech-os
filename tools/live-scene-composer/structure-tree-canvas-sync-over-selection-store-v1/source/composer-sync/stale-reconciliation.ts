
import { type EntityRef, type SceneGraphInput, type SelectionState, refKey, sceneRef, slotRef, layoutNodeRef } from "./contracts";

export interface RecoverySuggestion {
  readonly label: string;
  readonly ref: EntityRef;
  readonly reason: string;
}

export function resolveEntity(scene: SceneGraphInput, ref: EntityRef | null | undefined): boolean {
  if (!ref) return false;
  switch (ref.kind) {
    case "scene":
      return ref.sceneId === scene.sceneId;
    case "layout-node":
      return Boolean(scene.layoutNodes[ref.layoutNodeId]);
    case "slot":
      return Boolean(scene.slots[ref.slotId]);
    case "widget":
      return Boolean(scene.widgets[ref.widgetId]);
  }
}

export function reconcileSelection(scene: SceneGraphInput, selection: SelectionState): SelectionState {
  if (selection.status !== "active" || !selection.ref) {
    return selection;
  }
  if (selection.revision === scene.revision && resolveEntity(scene, selection.ref)) {
    return selection;
  }
  return {
    status: "stale",
    ref: selection.ref,
    revision: scene.revision,
    origin: selection.origin,
    staleReason: resolveEntity(scene, selection.ref) ? "revision-replaced" : "entity-missing"
  };
}

export function buildRecoverySuggestions(scene: SceneGraphInput, selection: SelectionState): readonly RecoverySuggestion[] {
  if (selection.status !== "stale" || !selection.ref) {
    return [];
  }

  const suggestions: RecoverySuggestion[] = [
    { label: "Select scene root", ref: sceneRef(scene.sceneId), reason: "safe-root-fallback" }
  ];

  if (selection.ref.kind === "widget") {
    const widget = scene.widgets[selection.ref.widgetId];
    if (widget) {
      suggestions.unshift({ label: "Select host slot", ref: slotRef(scene.sceneId, widget.slotId), reason: "host-slot-recovery" });
    }
  }

  if (selection.ref.kind === "slot") {
    for (const node of Object.values(scene.layoutNodes)) {
      if (node.slotId === selection.ref.slotId) {
        suggestions.unshift({ label: "Select layout ancestor", ref: layoutNodeRef(scene.sceneId, node.id), reason: "layout-ancestor-recovery" });
        break;
      }
    }
  }

  const unique = new Map<string, RecoverySuggestion>();
  for (const item of suggestions) {
    unique.set(refKey(item.ref), item);
  }
  return [...unique.values()];
}
