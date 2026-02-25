import type { IncomingMessage, ServerResponse } from "node:http";
import {
  GOVERNANCE_SUPPORTED_STAGE_IDS,
  createGovernanceStageSnapshot,
  normalizeRunId
} from "../contracts/governance.ts";
import type { CoreApiDependencies } from "../server.ts";
import { writeJson } from "../lib/http.ts";

export async function governanceStageRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  _deps: CoreApiDependencies,
  stageId: string
): Promise<void> {
  const snapshot = createGovernanceStageSnapshot(stageId);
  if (!snapshot) {
    writeJson(response, 404, {
      error: "GOVERNANCE_STAGE_NOT_FOUND",
      stageId: normalizeRunId(stageId),
      supportedStages: [...GOVERNANCE_SUPPORTED_STAGE_IDS]
    });
    return;
  }

  writeJson(response, 200, snapshot);
}

export async function governanceRunsRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  const payload = await deps.runIndex.listRuns();
  writeJson(response, 200, payload);
}

export async function governanceRunArtifactsRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies,
  runId: string
): Promise<void> {
  const payload = await deps.artifactStore.listRunArtifacts(runId);
  if (payload.status === "invalid_run_id") {
    writeJson(response, 400, payload);
    return;
  }

  writeJson(response, 200, payload);
}
