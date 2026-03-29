import type { ResolvedInspectorTarget, SceneDocument, SelectionTarget } from "../authoring-workbench-contracts";

export function deriveInspectorTarget(document: SceneDocument, selection: SelectionTarget | null): ResolvedInspectorTarget {
  if (!selection) {
    return {
      surface: "none",
      title: "No target",
      description: "Selection is empty. Choose a scene, layout node, slot, or widget.",
      selection: null,
      sections: [],
    };
  }
  if (selection.kind === "scene") {
    return {
      surface: "scene-look",
      title: document.scene.title,
      description: "Scene look controls remain distinct from selection state and only edit scene-level appearance.",
      selection,
      sections: ["background", "overlays", "visual effects", "stage style", "card style", "motion", "density"],
    };
  }
  if (selection.kind === "layout-node") {
    const node = document.layoutNodes[selection.id];
    return {
      surface: "layout-node",
      title: node?.title ?? selection.id,
      description: "Layout operations remain structural: move, resize, reorder, and reset.",
      selection,
      sections: ["frame", "ordering", "reset"],
    };
  }
  if (selection.kind === "slot") {
    const slot = document.slots[selection.id];
    return {
      surface: "slot",
      title: slot?.title ?? selection.id,
      description: "Slot editing stays bounded to host semantics and prefab insertion.",
      selection,
      sections: ["compatibility", "capacity", "prefabs"],
    };
  }
  const widget = document.widgets[selection.id];
  return {
    surface: "widget",
    title: widget?.title ?? selection.id,
    description: "Widget editing separates props from style and routes every write through the bridge.",
    selection,
    sections: ["props", "style", "removal", "reset"],
  };
}
