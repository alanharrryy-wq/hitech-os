
import { type BoundsRect, type CanvasOverlay, type CanvasViewModel, type EntityRef, type ObservedBoundsEntry, type SceneGraphInput, type SelectionState, refKey } from "./contracts";

function findRect(bounds: readonly ObservedBoundsEntry[], ref: EntityRef): BoundsRect | undefined {
  const hit = bounds.find((entry) => entry.refKey === refKey(ref) && entry.visible);
  return hit?.rect;
}

function overlayForSelection(selection: SelectionState, bounds: readonly ObservedBoundsEntry[]): CanvasOverlay[] {
  if (selection.status === "none" || !selection.ref) {
    return [];
  }

  const rect = findRect(bounds, selection.ref);
  if (selection.status === "stale") {
    return [{
      overlayId: `stale:${selection.ref.kind}`,
      kind: "stale-ghost",
      label: `Unavailable ${selection.ref.kind}`,
      rect,
      editable: false,
      notes: [selection.staleReason ?? "Selected target is stale."]
    }];
  }

  switch (selection.ref.kind) {
    case "scene":
      return [{ overlayId: "scene-frame", kind: "scene-frame", label: "Scene", rect, editable: false, notes: ["Scene-level framing only."] }];
    case "layout-node":
      return [
        { overlayId: "layout-frame", kind: "layout-frame", label: "Layout node", rect, editable: true, notes: ["May expose resize or reorder handles through intent builders."] },
        { overlayId: "layout-guides", kind: "guide", label: "Layout guides", rect, editable: false, notes: ["Guide lines only."] }
      ];
    case "slot":
      return [{ overlayId: "slot-frame", kind: "slot-frame", label: "Slot", rect, editable: true, notes: ["Insertion and occupancy framing."] }];
    case "widget":
      return [{ overlayId: "widget-frame", kind: "widget-frame", label: "Widget", rect, editable: true, notes: ["Widget focus frame and handles."] }];
  }
}

export function buildCanvasViewModel(input: { scene: SceneGraphInput; selection: SelectionState; bounds: readonly ObservedBoundsEntry[] }): CanvasViewModel {
  const overlays = overlayForSelection(input.selection, input.bounds);
  const diagnostics: string[] = [];

  if (input.selection.status === "none") {
    diagnostics.push("No active selection.");
  }
  if (input.selection.status === "stale") {
    diagnostics.push(`Selection stale: ${input.selection.staleReason ?? "unknown"}`);
  }
  if (input.selection.ref) {
    diagnostics.push(`Selected kind: ${input.selection.ref.kind}`);
  }
  if (overlays.length === 0 && input.selection.status === "active") {
    diagnostics.push("Selection active but no visible bounds found.");
  }

  return {
    selection: input.selection,
    overlays,
    emptyState: overlays.length === 0,
    diagnostics
  };
}
