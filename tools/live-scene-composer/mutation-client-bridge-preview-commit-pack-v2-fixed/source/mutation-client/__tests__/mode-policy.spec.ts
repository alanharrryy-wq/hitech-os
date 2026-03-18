import { buildPreviewEnvelope } from "../mutation-intents";
import { checkModePolicy } from "../mode-policy";

describe("checkModePolicy", () => {
  it("rejects advanced-only tags in safe mode", () => {
    const envelope = buildPreviewEnvelope({
      source: "inspector",
      type: "widget-style-update",
      mode: "safe",
      target: { kind: "widget", sceneId: "scene-a", widgetId: "widget-1" },
      payload: { color: "#fff" },
      tags: ["requires-advanced-capability"]
    });
    expect(checkModePolicy(envelope).length).toBeGreaterThan(0);
  });
});
