import { buildPreviewEnvelope } from "../mutation-intents";
import { validateMutationEnvelope } from "../validation";

describe("validateMutationEnvelope", () => {
  it("fails when target does not exist in validation context", () => {
    const envelope = buildPreviewEnvelope({
      source: "canvas",
      type: "widget-style-update",
      mode: "safe",
      target: { kind: "widget", sceneId: "scene-a", widgetId: "widget-404" },
      payload: { color: "#f00" }
    });
    const result = validateMutationEnvelope(envelope, { existingWidgetIds: ["widget-1"] });
    expect(result.ok).toBe(false);
  });
});
