
import { buildCanvasViewModel } from "../canvas-viewmodel";
import { buildMutationIntents } from "../mutation-intent-entrypoints";
import { createMiniBounds, createMiniScene, demoRefs } from "../scenario-fixtures";
import { buildStructureTreeProjection } from "../structure-tree-projection";

const scene = createMiniScene();
const selection = { status: "active", ref: demoRefs.widget, revision: scene.revision, origin: "canvas" } as const;

const tree = buildStructureTreeProjection(scene, selection);
const canvas = buildCanvasViewModel({ scene, selection, bounds: createMiniBounds() });
const intents = buildMutationIntents(selection);

console.log(JSON.stringify({
  activeRefKind: selection.ref.kind,
  treeFlatOrder: tree.flatOrder.length,
  overlayKinds: canvas.overlays.map((item) => item.kind),
  intentTypes: intents.map((item) => item.type)
}, null, 2));
