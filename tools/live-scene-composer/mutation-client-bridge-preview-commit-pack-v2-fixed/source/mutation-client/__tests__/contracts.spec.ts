import { targetKey } from "../contracts";

describe("targetKey", () => {
  it("formats widget targets deterministically", () => {
    expect(targetKey({ kind: "widget", sceneId: "scene-a", widgetId: "widget-1" })).toBe("widget:scene-a:widget-1");
  });
});
