import { buildPreviewEnvelope } from "../mutation-intents";
import { buildRevertPlan } from "../revert-planner";

describe("buildRevertPlan", () => {
  it("builds a snapshot strategy for structural changes", () => {
    const envelope = buildPreviewEnvelope({
      source: "structure-tree",
      type: "slot-insert-widget",
      mode: "safe",
      target: { kind: "slot", sceneId: "scene-a", slotId: "slot-1" },
      payload: { prefabId: "prefab-kpi" }
    });
    const plan = buildRevertPlan([envelope], { kind: "slot", sceneId: "scene-a", slotId: "slot-1" });
    expect(plan.strategy).toBe("snapshot-restore");
  });
});
