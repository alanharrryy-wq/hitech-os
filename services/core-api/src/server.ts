import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import type { FeatureFlags } from "./contracts.ts";
import { FEATURE_FLAGS_DEFAULTS } from "./contracts.ts";
import { AiAgentClient } from "./lib/aiAgentClient.ts";
import { loadRuntimeConfig, type CoreApiRuntimeConfig } from "./lib/config.ts";
import { DeterministicJobQueue } from "./lib/jobQueue.ts";
import { getHttpContext, matchPath, writeNotFound } from "./lib/http.ts";
import { capabilitiesRoute } from "./routes/capabilities.ts";
import { flagsRoute } from "./routes/flags.ts";
import { healthRoute } from "./routes/health.ts";
import { getJobRoute, postJobsRoute, runJobRoute } from "./routes/jobs.ts";

export interface BuildServerOptions {
  runtimeConfig?: Partial<CoreApiRuntimeConfig>;
  featureFlags?: Partial<FeatureFlags>;
  queue?: DeterministicJobQueue;
  agentClient?: AiAgentClient;
}

export interface CoreApiDependencies {
  runtimeConfig: CoreApiRuntimeConfig;
  featureFlags: FeatureFlags;
  queue: DeterministicJobQueue;
  agentClient: AiAgentClient;
}

export interface CoreApiServer {
  server: Server;
  deps: CoreApiDependencies;
}

function createDependencies(options: BuildServerOptions): CoreApiDependencies {
  const runtimeDefaults = loadRuntimeConfig();
  const runtimeConfig: CoreApiRuntimeConfig = {
    ...runtimeDefaults,
    ...(options.runtimeConfig ?? {})
  };

  const featureFlags: FeatureFlags = {
    ...FEATURE_FLAGS_DEFAULTS,
    ...(options.featureFlags ?? {})
  };

  const queue = options.queue ?? new DeterministicJobQueue();
  const agentClient =
    options.agentClient ??
    new AiAgentClient({
      baseUrl: runtimeConfig.aiAgentUrl,
      timeoutMs: runtimeConfig.aiAgentTimeoutMs
    });

  return {
    runtimeConfig,
    featureFlags,
    queue,
    agentClient
  };
}

async function handleRequest(
  request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  const context = getHttpContext(request);

  if (context.method === "GET" && context.pathname === "/health") {
    await healthRoute(request, response, deps);
    return;
  }

  if (context.method === "GET" && context.pathname === "/flags") {
    await flagsRoute(request, response, deps);
    return;
  }

  if (context.method === "GET" && context.pathname === "/capabilities") {
    await capabilitiesRoute(request, response, deps);
    return;
  }

  if (context.method === "POST" && context.pathname === "/jobs") {
    await postJobsRoute(request, response, deps);
    return;
  }

  const getMatch = matchPath(context.pathname, "/jobs/:id");
  if (context.method === "GET" && getMatch) {
    await getJobRoute(request, response, deps, getMatch.params.id);
    return;
  }

  const runMatch = matchPath(context.pathname, "/jobs/:id/run");
  if (context.method === "POST" && runMatch) {
    await runJobRoute(request, response, deps, runMatch.params.id);
    return;
  }

  writeNotFound(response, context.pathname);
}

export function buildServer(options: BuildServerOptions = {}): CoreApiServer {
  const deps = createDependencies(options);
  const server = createServer((request, response) => {
    void handleRequest(request, response, deps).catch((error) => {
      response.statusCode = 500;
      response.setHeader("content-type", "application/json; charset=utf-8");
      response.end(
        `${JSON.stringify(
          {
            error: "INTERNAL_SERVER_ERROR",
            message: error instanceof Error ? error.message : "unknown error"
          },
          null,
          2
        )}\n`
      );
    });
  });

  return {
    server,
    deps
  };
}
