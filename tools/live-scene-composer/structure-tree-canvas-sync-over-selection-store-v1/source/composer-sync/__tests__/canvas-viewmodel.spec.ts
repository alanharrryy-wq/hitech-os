
import { buildCanvasViewModel } from "../canvas-viewmodel";
import { createMiniBounds, createMiniScene, demoRefs } from "../scenario-fixtures";

describe("buildCanvasViewModel", () => {
  it("creates editable overlays for active widget selection", () => {
    const viewModel = buildCanvasViewModel({
      scene: createMiniScene(),
      selection: { status: "active", ref: demoRefs.widget, revision: "rev-001", origin: "canvas" },
      bounds: createMiniBounds()
    });
    expect(viewModel.overlays[0]?.kind).toBe("widget-frame");
    expect(viewModel.overlays[0]?.editable).toBe(true);
  });

  it("suppresses editable overlays when selection is stale", () => {
    const viewModel = buildCanvasViewModel({
      scene: createMiniScene(),
      selection: { status: "stale", ref: demoRefs.widget, revision: "rev-002", origin: "canvas", staleReason: "entity-missing" },
      bounds: createMiniBounds()
    });
    expect(viewModel.overlays[0]?.kind).toBe("stale-ghost");
    expect(viewModel.overlays[0]?.editable).toBe(false);
  });
});
