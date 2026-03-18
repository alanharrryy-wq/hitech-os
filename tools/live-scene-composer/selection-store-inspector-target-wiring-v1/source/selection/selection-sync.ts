import { type SelectionState, type SurfaceSyncInstruction, type SurfaceSyncPlan } from "./contracts";

export function buildSelectionSurfaceSyncPlan(selection: SelectionState): SurfaceSyncPlan {
  const instructions: SurfaceSyncInstruction[] = [];

  if (selection.status === "none") {
    instructions.push(
      { surface: "canvas", action: "clear", ref: null, notes: ["Remove overlays and handles."] },
      { surface: "structure-tree", action: "clear", ref: null, notes: ["Clear active-node highlight."] },
      { surface: "inspector", action: "show-empty", ref: null, notes: ["Render empty-editor state."] }
    );
    return { selection, instructions };
  }

  if (selection.status === "stale") {
    instructions.push(
      { surface: "canvas", action: "clear", ref: selection.ref, notes: ["Target-specific affordances must disappear immediately."] },
      { surface: "structure-tree", action: "clear", ref: selection.ref, notes: ["Do not pretend the stale target is still active."] },
      { surface: "inspector", action: "show-unavailable", ref: selection.ref, notes: ["Display recovery messaging instead of editable controls."] }
    );
    return { selection, instructions };
  }

  switch (selection.ref.kind) {
    case "scene":
      instructions.push(
        { surface: "canvas", action: "highlight-scene", ref: selection.ref, notes: ["Frame the scene shell or stage."] },
        { surface: "structure-tree", action: "highlight-scene", ref: selection.ref, notes: ["Focus the scene root node."] },
        { surface: "inspector", action: "show-ready", ref: selection.ref, notes: ["Show scene-editor."] }
      );
      break;
    case "layout-node":
      instructions.push(
        { surface: "canvas", action: "highlight-layout-node", ref: selection.ref, notes: ["Show layout overlays and handles."] },
        { surface: "structure-tree", action: "highlight-layout-node", ref: selection.ref, notes: ["Focus the matching layout node."] },
        { surface: "inspector", action: "show-ready", ref: selection.ref, notes: ["Show layout-node-editor."] }
      );
      break;
    case "slot":
      instructions.push(
        { surface: "canvas", action: "highlight-slot", ref: selection.ref, notes: ["Show slot boundary and occupancy framing."] },
        { surface: "structure-tree", action: "highlight-slot", ref: selection.ref, notes: ["Focus the matching slot node."] },
        { surface: "inspector", action: "show-ready", ref: selection.ref, notes: ["Show slot-editor."] }
      );
      break;
    case "widget":
      instructions.push(
        { surface: "canvas", action: "highlight-widget", ref: selection.ref, notes: ["Show widget overlay and target handles."] },
        { surface: "structure-tree", action: "highlight-widget", ref: selection.ref, notes: ["Focus the matching widget node."] },
        { surface: "inspector", action: "show-ready", ref: selection.ref, notes: ["Show widget-editor."] }
      );
      break;
  }

  return { selection, instructions };
}

export function summarizeSurfaceSyncPlan(plan: SurfaceSyncPlan): readonly string[] {
  return plan.instructions.map((instruction) => {
    const refLabel = instruction.ref ? instruction.ref.kind : "none";
    return `${instruction.surface}:${instruction.action}:${refLabel}`;
  });
}
