import { DefaultBridgeClient } from "../bridge-client";
import { buildCommitEnvelope } from "../mutation-intents";
import { openPreviewSession } from "../preview-session";
import { previewThenCommit } from "../commit-orchestrator";

describe("previewThenCommit", () => {
  it("runs preview then commit", async () => {
    const client = new DefaultBridgeClient();
    const session = openPreviewSession({ sceneId: "scene-a", baselineRevision: "base", draftRevision: "draft" });
    const envelope = buildCommitEnvelope({
      source: "inspector",
      type: "scene-look-update",
      mode: "safe",
      target: { kind: "scene", sceneId: "scene-a" },
      payload: { color: "#111" },
      previewSessionId: session.sessionId
    });
    const result = await previewThenCommit(client, session, envelope, { existingSceneIds: ["scene-a"] });
    expect(result.commitDecision?.accepted).toBe(true);
  });
});
