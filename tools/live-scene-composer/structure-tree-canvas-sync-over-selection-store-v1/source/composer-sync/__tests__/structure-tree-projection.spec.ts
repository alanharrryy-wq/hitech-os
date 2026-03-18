
import { buildStructureTreeProjection } from "../structure-tree-projection";
import { createMiniScene, demoRefs } from "../scenario-fixtures";

describe("buildStructureTreeProjection", () => {
  it("preserves scene root and nested slot/widget relationships", () => {
    const projection = buildStructureTreeProjection(createMiniScene(), { status: "active", ref: demoRefs.slot, revision: "rev-001", origin: "structure-tree" });
    expect(projection.root.kind).toBe("scene");
    expect(projection.flatOrder.length).toBeGreaterThan(4);
    expect(JSON.stringify(projection.root)).toContain("slot-chart");
    expect(JSON.stringify(projection.root)).toContain("widget-chart-1");
  });
});
