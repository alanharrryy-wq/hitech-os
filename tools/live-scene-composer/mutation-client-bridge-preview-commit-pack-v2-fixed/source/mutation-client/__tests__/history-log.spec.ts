import { MutationHistoryLog, toHistoryEntry } from "../history-log";
import { buildPreviewEnvelope } from "../mutation-intents";

describe("MutationHistoryLog", () => {
  it("stores entries", () => {
    const log = new MutationHistoryLog();
    const envelope = buildPreviewEnvelope({
      source: "inspector",
      type: "scene-look-update",
      mode: "safe",
      target: { kind: "scene", sceneId: "scene-a" },
      payload: { background: "#000" }
    });
    log.append(toHistoryEntry(envelope, {
      accepted: true,
      decisionKind: "preview-approved",
      mutationId: envelope.mutationId,
      diagnostics: ["ok"]
    }));
    expect(log.all()).toHaveLength(1);
  });
});
