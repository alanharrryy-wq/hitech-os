import { InMemoryBridgeAdapter } from "../bridge-adapter";
import { buildPreviewEnvelope } from "../mutation-intents";

describe("InMemoryBridgeAdapter", () => {
  it("rejects widget-remove preview in safe mode", async () => {
    const adapter = new InMemoryBridgeAdapter();
    const envelope = buildPreviewEnvelope({
      source: "canvas",
      type: "widget-remove",
      mode: "safe",
      target: { kind: "widget", sceneId: "scene-a", widgetId: "widget-1" },
      payload: { hard: false }
    });
    const result = await adapter.handle({ envelope, action: "preview" });
    expect(result.accepted).toBe(false);
  });
});
