import type { IncomingMessage, ServerResponse } from "node:http";
import type { CoreApiDependencies } from "../server.ts";
import { validateJobRequest } from "../contracts.ts";
import { readJsonBody, writeJson } from "../lib/http.ts";

export async function postJobsRoute(
  request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies
): Promise<void> {
  let body: unknown;
  try {
    body = await readJsonBody(request);
  } catch {
    writeJson(response, 400, {
      error: "INVALID_JSON",
      message: "Request body must be valid JSON"
    });
    return;
  }

  const parsed = validateJobRequest(body);
  if (!parsed.ok || parsed.value === undefined) {
    writeJson(response, 400, {
      error: "INVALID_JOB_REQUEST",
      issues: parsed.issues
    });
    return;
  }

  const queued = deps.queue.enqueue(parsed.value);
  writeJson(response, 202, queued.result);
}

export async function getJobRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies,
  jobId: string
): Promise<void> {
  const state = deps.queue.get(jobId);
  if (!state) {
    writeJson(response, 404, {
      error: "JOB_NOT_FOUND",
      jobId
    });
    return;
  }

  writeJson(response, 200, state.result);
}

export async function runJobRoute(
  _request: IncomingMessage,
  response: ServerResponse,
  deps: CoreApiDependencies,
  jobId: string
): Promise<void> {
  const state = deps.queue.get(jobId);
  if (!state) {
    writeJson(response, 404, {
      error: "JOB_NOT_FOUND",
      jobId
    });
    return;
  }

  if (state.result.status === "completed") {
    writeJson(response, 200, state.result);
    return;
  }

  if (state.result.status === "failed") {
    writeJson(response, 409, state.result);
    return;
  }

  const now = deps.clock.nowUtcIso();

  if (!state.request.flags.enableAiExecution) {
    const skipped = deps.queue.markSkipped(
      jobId,
      now,
      "Execution blocked because enableAiExecution is false for this job"
    );
    writeJson(response, 409, {
      error: "FEATURE_FLAG_DISABLED",
      result: skipped?.result ?? state.result
    });
    return;
  }

  deps.queue.markRunning(jobId, now);
  const result = await deps.agentClient.runJob(state.request);

  if (!result.ok) {
    const failed = deps.queue.markFinished({
      jobId,
      status: "failed",
      output: {
        errorCode: result.errorCode,
        message: result.message
      },
      atUtc: deps.clock.nowUtcIso(),
      event: "job.failed",
      message: `ai-agent call failed (${result.errorCode})`
    });

    writeJson(response, 502, {
      error: "AGENT_EXECUTION_FAILED",
      reason: result,
      result: failed?.result ?? state.result
    });
    return;
  }

  const completed = deps.queue.markFinished({
    jobId,
    status: "completed",
    output: result.data.output,
    atUtc: result.data.finishedAtUtc ?? deps.clock.nowUtcIso(),
    event: "job.completed",
    message: "ai-agent returned deterministic output"
  });

  const payload = completed?.result ?? result.data;
  writeJson(response, 200, payload);
}
