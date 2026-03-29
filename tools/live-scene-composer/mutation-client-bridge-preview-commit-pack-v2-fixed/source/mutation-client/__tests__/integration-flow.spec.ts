import { DefaultBridgeClient } from "../bridge-client";
import { createWidgetStyleScenario } from "../scenario-fixtures";
import { diagnosticsFromDecision } from "../diagnostics";

describe("integration flow", () => {
  it("produces diagnostics for preview decisions", async () => {
    const client = new DefaultBridgeClient();
    const scenario = createWidgetStyleScenario();
    const decision = await client.send({ envelope: scenario.previewEnvelope, action: "preview" });
    expect(diagnosticsFromDecision(decision)[0].category).toBe("bridge-preview");
  });
});
