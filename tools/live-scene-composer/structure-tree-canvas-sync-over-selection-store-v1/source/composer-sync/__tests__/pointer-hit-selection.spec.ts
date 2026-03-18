
import { pickBestCanvasHit } from "../pointer-hit-selection";
import { createMiniScene } from "../scenario-fixtures";

describe("pickBestCanvasHit", () => {
  it("prefers widget over slot over layout over scene", () => {
    const result = pickBestCanvasHit(createMiniScene(), [
      { kind: "scene", id: "scene-demo" },
      { kind: "slot", id: "slot-chart" },
      { kind: "widget", id: "widget-chart-1", slotId: "slot-chart" }
    ]);
    expect(result?.kind).toBe("widget");
  });
});
