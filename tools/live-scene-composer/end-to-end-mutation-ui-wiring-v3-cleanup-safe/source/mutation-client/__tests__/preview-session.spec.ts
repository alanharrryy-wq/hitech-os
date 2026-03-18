import { buildPreviewEnvelope } from "../mutation-intents";
import { openPreviewSession, stageEnvelope, discardPreviewSession } from "../preview-session";

describe("preview session", () => {
  it("stages then discards", () => {
    const session = openPreviewSession({ sceneId: "scene-a", baselineRevision: "base", draftRevision: "draft" });
    const staged = stageEnvelope(session, buildPreviewEnvelope({
      source: "inspector",
      type: "scene-look-update",
      mode: "safe",
      target: { kind: "scene", sceneId: "scene-a" },
      payload: { background: "#000" }
    }), { background: "#000" });
    expect(staged.commitReady).toBe(true);
    expect(discardPreviewSession(staged).pendingEnvelopes).toHaveLength(0);
  });
});
