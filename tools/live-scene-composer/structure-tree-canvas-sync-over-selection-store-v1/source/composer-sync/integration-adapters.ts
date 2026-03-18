
import { buildCanvasViewModel } from "./canvas-viewmodel";
import { type ObservedBoundsEntry, type SceneGraphInput, type SelectionState } from "./contracts";
import { buildStructureTreeProjection } from "./structure-tree-projection";

export interface SurfaceAdapters {
  readonly buildTree: (selection: SelectionState) => ReturnType<typeof buildStructureTreeProjection>;
  readonly buildCanvas: (selection: SelectionState, bounds: readonly ObservedBoundsEntry[]) => ReturnType<typeof buildCanvasViewModel>;
}

export function createSurfaceAdapters(scene: SceneGraphInput): SurfaceAdapters {
  return {
    buildTree(selection) {
      return buildStructureTreeProjection(scene, selection);
    },
    buildCanvas(selection, bounds) {
      return buildCanvasViewModel({ scene, selection, bounds });
    }
  };
}
