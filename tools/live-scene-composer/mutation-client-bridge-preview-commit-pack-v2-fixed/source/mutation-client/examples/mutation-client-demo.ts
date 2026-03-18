import {
  DefaultBridgeClient,
  createSceneLookScenario,
  diagnosticsFromDecision,
  previewThenCommit,
  MutationHistoryLog,
  toHistoryEntry
} from "../index";

async function runDemo() {
  const client = new DefaultBridgeClient();
  const history = new MutationHistoryLog();
  const scenario = createSceneLookScenario();

  const result = await previewThenCommit(client, scenario.session, scenario.commitEnvelope, {
    existingSceneIds: ["scene-home"]
  });

  if (result.previewDecision) {
    history.append(toHistoryEntry(scenario.commitEnvelope, result.previewDecision));
    console.log("preview diagnostics", diagnosticsFromDecision(result.previewDecision));
  }
  if (result.commitDecision) {
    history.append(toHistoryEntry(scenario.commitEnvelope, result.commitDecision));
    console.log("commit diagnostics", diagnosticsFromDecision(result.commitDecision));
  }

  console.log("history entries", history.all());
}

void runDemo();
