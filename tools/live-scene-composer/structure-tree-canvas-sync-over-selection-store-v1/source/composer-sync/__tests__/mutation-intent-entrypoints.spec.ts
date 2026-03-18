
import { buildMutationIntents, summarizeMutationCapabilities } from "../mutation-intent-entrypoints";
import { createMiniScene, demoRefs } from "../scenario-fixtures";

describe("mutation intent entrypoints", () => {
  it("enables widget edit intents for widget selection", () => {
    const caps = summarizeMutationCapabilities({ status: "active", ref: demoRefs.widget, revision: "rev-001", origin: "canvas" });
    expect(caps.canEditWidgetProps).toBe(true);
    expect(buildMutationIntents({ status: "active", ref: demoRefs.widget, revision: "rev-001", origin: "canvas" }).length).toBeGreaterThan(1);
  });

  it("disables intents for stale selection", () => {
    expect(buildMutationIntents({ status: "stale", ref: demoRefs.widget, revision: "rev-002", origin: "canvas", staleReason: "entity-missing" }).length).toBe(0);
  });
});
