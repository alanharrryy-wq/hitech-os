import { DefaultBridgeClient } from "../bridge-client";
import { buildPreviewEnvelope } from "../mutation-intents";

describe("DefaultBridgeClient", () => {
  it("returns a preview decision", async () => {
    const client = new DefaultBridgeClient();
    const envelope = buildPreviewEnvelope({
      source: "canvas",
      type: "widget-style-update",
      mode: "safe",
      target: { kind: "widget", sceneId: "scene-a", widgetId: "widget-1" },
      payload: { color: "#0f0" }
    });
    const decision = await client.send({ envelope, action: "preview" });
    expect(decision.decisionKind).toBe("preview-approved");
  });
});
