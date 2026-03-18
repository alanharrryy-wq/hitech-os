
import { createSurfaceCoordinator } from "../surface-coordinator";
import { createMiniBounds, createMiniScene, demoRefs } from "../scenario-fixtures";

function createMemoryStore() {
  let selection = { status: "none", ref: null, revision: null, origin: null } as any;
  return {
    getSnapshot() { return { selection }; },
    select(input: any) { selection = { status: "active", ref: input.ref, revision: input.revision, origin: input.origin }; },
    clear(reason?: string, origin?: string) { selection = { status: "none", ref: null, revision: null, origin: origin ?? null }; },
    markStale(reason: string, revision?: string) { selection = { ...selection, status: "stale", revision: revision ?? selection.revision, staleReason: reason }; }
  };
}

describe("surface coordinator", () => {
  it("synchronizes tree and canvas instructions after tree selection", () => {
    const store = createMemoryStore();
    const coordinator = createSurfaceCoordinator({ store, scene: createMiniScene(), observedBounds: createMiniBounds() });
    const snapshot = coordinator.dispatch({ kind: "tree-select", origin: "structure-tree", ref: demoRefs.widget, revision: "rev-001" });
    expect(snapshot.instructions.some((item) => item.surface === "canvas")).toBe(true);
    expect(snapshot.instructions.some((item) => item.surface === "structure-tree")).toBe(true);
  });
});
