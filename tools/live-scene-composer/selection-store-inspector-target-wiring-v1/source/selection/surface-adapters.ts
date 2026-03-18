import { type SelectionInput, type SelectionRef } from "./contracts";

export interface CanvasHitResult {
  readonly target: SelectionRef | null;
  readonly revision: string;
  readonly breadcrumb?: readonly string[];
}

export interface StructureTreeNodeSelection {
  readonly target: SelectionRef;
  readonly revision: string;
  readonly breadcrumb?: readonly string[];
}

export function canvasHitToSelectionInput(hit: CanvasHitResult): SelectionInput | null {
  if (!hit.target) {
    return null;
  }
  return {
    ref: hit.target,
    origin: "canvas",
    revision: hit.revision,
    context: {
      breadcrumb: hit.breadcrumb
    },
    reason: "surface-select"
  };
}

export function structureTreeNodeToSelectionInput(node: StructureTreeNodeSelection): SelectionInput {
  return {
    ref: node.target,
    origin: "structure-tree",
    revision: node.revision,
    context: {
      breadcrumb: node.breadcrumb
    },
    reason: "surface-select"
  };
}
