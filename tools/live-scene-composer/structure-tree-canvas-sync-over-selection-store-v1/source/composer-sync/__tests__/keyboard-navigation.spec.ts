
import { moveTreeFocus } from "../keyboard-navigation";
import { buildStructureTreeProjection } from "../structure-tree-projection";
import { createMiniScene, demoRefs } from "../scenario-fixtures";

describe("moveTreeFocus", () => {
  it("moves deterministically through projection order", () => {
    const projection = buildStructureTreeProjection(createMiniScene(), { status: "active", ref: demoRefs.scene, revision: "rev-001", origin: "system" });
    const first = moveTreeFocus(projection, null, "home");
    const second = moveTreeFocus(projection, first, "down");
    expect(first).not.toBeNull();
    expect(second).not.toBeNull();
  });
});
