
import { type EntityRef, type SceneGraphInput, layoutNodeRef, sceneRef, slotRef, widgetRef } from "./contracts";

export interface CanvasHitCandidate {
  readonly kind: "scene" | "layout-node" | "slot" | "widget";
  readonly id: string;
  readonly slotId?: string;
}

const priorityOrder = ["widget", "slot", "layout-node", "scene"] as const;

export function pickBestCanvasHit(scene: SceneGraphInput, candidates: readonly CanvasHitCandidate[]): EntityRef | null {
  const ordered = [...candidates].sort((a, b) => priorityOrder.indexOf(a.kind) - priorityOrder.indexOf(b.kind));
  const hit = ordered[0];
  if (!hit) return null;
  switch (hit.kind) {
    case "scene":
      return sceneRef(scene.sceneId);
    case "layout-node":
      return layoutNodeRef(scene.sceneId, hit.id);
    case "slot":
      return slotRef(scene.sceneId, hit.id);
    case "widget":
      return widgetRef(scene.sceneId, hit.id, hit.slotId);
  }
}
