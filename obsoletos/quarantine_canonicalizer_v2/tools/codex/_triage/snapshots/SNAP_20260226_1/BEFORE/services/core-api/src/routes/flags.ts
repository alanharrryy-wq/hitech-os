import type { IncomingMessage, ServerResponse } from "node:http";
import type { CoreApiDependencies } from "../server.ts";
import { writeJson } from "../lib/http.ts";

export async function flagsRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  writeJson(response, 200, deps.featureFlags);
}
