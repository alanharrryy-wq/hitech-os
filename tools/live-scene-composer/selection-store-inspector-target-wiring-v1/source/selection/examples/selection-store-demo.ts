import {
  createLayoutNodeRef,
  createSceneRef,
  createWidgetRef
} from "../contracts";
import { deriveInspectorTarget } from "../inspector-target";
import { createSelectionStore } from "../selection-store";
import { buildSelectionSurfaceSyncPlan } from "../selection-sync";

const store = createSelectionStore();

store.subscribe((snapshot) => {
  console.log("selection", snapshot.selection);
  console.log("inspector", deriveInspectorTarget(snapshot.selection));
  console.log("sync-plan", buildSelectionSurfaceSyncPlan(snapshot.selection));
});

store.select({
  ref: createSceneRef("scene-dashboard"),
  origin: "system",
  revision: "rev-100",
  reason: "initial-select"
});

store.select({
  ref: createLayoutNodeRef("scene-dashboard", "layout-hero"),
  origin: "structure-tree",
  revision: "rev-100"
});

store.select({
  ref: createWidgetRef("scene-dashboard", "widget-revenue", "slot-hero-left"),
  origin: "canvas",
  revision: "rev-100"
});

store.markStale("revision-replaced", "rev-101");
