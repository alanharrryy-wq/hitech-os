import type { CanvasBox, ResolvedInspectorTarget, RuntimeObservationSnapshot, SceneDocument, SelectionTarget } from "../authoring-workbench-contracts";
import { buildCanvasBoxes } from "../model/scene-graph";
import { getObservedBounds } from "../runtime/runtime-observation";

export interface CanvasOverlayModel {
  readonly boxes: readonly CanvasBox[];
  readonly selectedFrame: { readonly x: number; readonly y: number; readonly width: number; readonly height: number } | null;
  readonly inspectorHint: string;
  readonly showGrid: boolean;
  readonly showSafeAreas: boolean;
}

export function createCanvasOverlayModel(
  document: SceneDocument,
  selection: SelectionTarget | null,
  inspectorTarget: ResolvedInspectorTarget,
  runtimeObserved: RuntimeObservationSnapshot
): CanvasOverlayModel {
  const boxes = buildCanvasBoxes(document, selection);
  const observedBounds = getObservedBounds(runtimeObserved, selection);
  return {
    boxes,
    selectedFrame: observedBounds?.frame ?? null,
    inspectorHint: inspectorTarget.description,
    showGrid: document.scene.look.overlays.grid,
    showSafeAreas: document.scene.look.overlays.safeAreas,
  };
}
