import type { IncomingMessage, ServerResponse } from "node:http";
import type { CoreApiDependencies } from "../server.ts";
import { writeJson } from "../lib/http.ts";

export async function capabilitiesRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  const result = await deps.agentClient.getCapabilities();

  if (!result.ok) {
    writeJson(response, 502, {
      error: "AGENT_CAPABILITIES_UNAVAILABLE",
      reason: {
        code: result.errorCode,
        statusCode: result.statusCode,
        message: result.message
      }
    });
    return;
  }

  writeJson(response, 200, result.data);
}
