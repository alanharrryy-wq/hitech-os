import type { RuntimeObservationSnapshot, RuntimeObservedBounds, SceneDocument, SelectionTarget } from "../authoring-workbench-contracts";
import { buildCanvasBoxes } from "../model/scene-graph";

export function createRuntimeObservationFromDocument(document: SceneDocument, selection: SelectionTarget | null): RuntimeObservationSnapshot {
  const boxes = buildCanvasBoxes(document, selection);
  const bounds: RuntimeObservedBounds[] = boxes.map((box) => ({
    targetKind: box.kind,
    targetId: box.id,
    frame: box.frame,
  }));
  return {
    sceneId: document.scene.id,
    bounds,
    measuredAtIso: new Date().toISOString(),
  };
}

export function getObservedBounds(snapshot: RuntimeObservationSnapshot, target: SelectionTarget | null): RuntimeObservedBounds | null {
  if (!target) {
    return null;
  }
  return snapshot.bounds.find((item) => item.targetId === target.id && item.targetKind === target.kind) ?? null;
}
