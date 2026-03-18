
import { buildRecoverySuggestions, reconcileSelection } from "../stale-reconciliation";
import { createMiniScene, demoRefs } from "../scenario-fixtures";

describe("stale reconciliation", () => {
  it("marks selection stale on revision mismatch", () => {
    const scene = createMiniScene();
    const result = reconcileSelection(scene, { status: "active", ref: demoRefs.widget, revision: "older-rev", origin: "canvas" });
    expect(result.status).toBe("stale");
  });

  it("offers safe recovery suggestions", () => {
    const scene = createMiniScene();
    const suggestions = buildRecoverySuggestions(scene, { status: "stale", ref: demoRefs.slot, revision: scene.revision, origin: "canvas", staleReason: "entity-missing" });
    expect(suggestions.length).toBeGreaterThan(0);
  });
});
