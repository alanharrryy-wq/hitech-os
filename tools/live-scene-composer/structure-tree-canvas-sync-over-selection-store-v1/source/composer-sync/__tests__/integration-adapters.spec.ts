
import { createSurfaceAdapters } from "../integration-adapters";
import { createMiniBounds, createMiniScene, demoRefs } from "../scenario-fixtures";

describe("surface adapters", () => {
  it("builds both tree and canvas projections from one scene input", () => {
    const scene = createMiniScene();
    const adapters = createSurfaceAdapters(scene);
    const selection = { status: "active", ref: demoRefs.grid, revision: scene.revision, origin: "system" } as const;
    const tree = adapters.buildTree(selection);
    const canvas = adapters.buildCanvas(selection, createMiniBounds());
    expect(tree.root.kind).toBe("scene");
    expect(canvas.diagnostics.length).toBeGreaterThan(0);
  });
});
