import type { IncomingMessage, ServerResponse } from "node:http";
import type { HealthCheck } from "../contracts.ts";
import { buildHealthReport } from "../contracts.ts";
import type { CoreApiDependencies } from "../server.ts";
import { writeJson } from "../lib/http.ts";

export async function healthRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  const snapshot = deps.queue.snapshot();
  const checks: HealthCheck[] = [
    {
      name: "contracts",
      status: "ok",
      message: `contract version ${deps.runtimeConfig.contractVersion}`
    },
    {
      name: "queue",
      status: "ok",
      message: `queued=${snapshot.queued} running=${snapshot.running} completed=${snapshot.completed} failed=${snapshot.failed}`
    }
  ];

  const agentHealth = await deps.agentClient.health();
  if (!agentHealth.ok) {
    checks.push({
      name: "ai-agent",
      status: "degraded",
      message: `${agentHealth.errorCode} (${agentHealth.statusCode})`
    });
  } else {
    checks.push({
      name: "ai-agent",
      status: "ok",
      message: `reachable:${agentHealth.data.service}`
    });
  }

  const report = buildHealthReport({
    service: "core-api",
    version: deps.runtimeConfig.serviceVersion,
    contractVersion: deps.runtimeConfig.contractVersion,
    checks,
    timestampUtc: deps.clock.nowUtcIso()
  });
  writeJson(response, 200, report);
}
