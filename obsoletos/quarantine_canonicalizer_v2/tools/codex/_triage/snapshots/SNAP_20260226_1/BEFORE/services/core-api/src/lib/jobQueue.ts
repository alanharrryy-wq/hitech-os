import type { JsonValue, JobRequest, JobResult, JobStatus, StructuredLog } from "../contracts.ts";
import { normalizeUtcIso } from "./deterministic.ts";

export interface QueuedJobState {
  enqueueSeq: number;
  request: JobRequest;
  result: JobResult;
  lastUpdatedUtc: string;
}

export interface QueueSnapshot {
  queued: number;
  running: number;
  completed: number;
  failed: number;
  total: number;
}

interface LogInput {
  level: "info" | "warn" | "error";
  event: string;
  message: string;
  atUtc: string;
  details?: Record<string, JsonValue>;
}

function buildInitialResult(request: JobRequest): JobResult {
  return {
    jobId: request.jobId,
    kind: request.kind,
    status: "queued",
    output: {},
    logs: [
      {
        seq: 0,
        level: "info",
        event: "job.enqueued",
        message: "Job accepted into deterministic queue",
        atUtc: request.requestedAtUtc,
        details: {
          kind: request.kind
        }
      }
    ],
    finishedAtUtc: null
  };
}

function appendLog(existing: StructuredLog[], input: LogInput): StructuredLog[] {
  const next: StructuredLog = {
    seq: existing.length,
    level: input.level,
    event: input.event,
    message: input.message,
    atUtc: normalizeUtcIso(input.atUtc),
    details: input.details ?? {}
  };

  return [...existing, next];
}

function compareJobs(left: QueuedJobState, right: QueuedJobState): number {
  const leftTime = left.request.requestedAtUtc;
  const rightTime = right.request.requestedAtUtc;
  const byTime = leftTime.localeCompare(rightTime);
  if (byTime !== 0) {
    return byTime;
  }

  const byId = left.request.jobId.localeCompare(right.request.jobId);
  if (byId !== 0) {
    return byId;
  }

  return left.enqueueSeq - right.enqueueSeq;
}

export class DeterministicJobQueue {
  #sequence = 0;
  #states = new Map<string, QueuedJobState>();

  enqueue(request: JobRequest): QueuedJobState {
    const existing = this.#states.get(request.jobId);
    if (existing) {
      return existing;
    }

    const now = normalizeUtcIso(request.requestedAtUtc);
    const created: QueuedJobState = {
      enqueueSeq: this.#sequence,
      request: {
        ...request,
        requestedAtUtc: now
      },
      result: buildInitialResult({
        ...request,
        requestedAtUtc: now
      }),
      lastUpdatedUtc: now
    };

    this.#sequence += 1;
    this.#states.set(request.jobId, created);
    return created;
  }

  get(jobId: string): QueuedJobState | undefined {
    return this.#states.get(jobId);
  }

  getOrdered(): QueuedJobState[] {
    return [...this.#states.values()].sort(compareJobs);
  }

  getNextRunnable(): QueuedJobState | null {
    const next = this.getOrdered().find((item) => item.result.status === "queued");
    return next ?? null;
  }

  markRunning(jobId: string, atUtc: string): QueuedJobState | null {
    const current = this.#states.get(jobId);
    if (!current) {
      return null;
    }

    if (current.result.status !== "queued") {
      return current;
    }

    const normalized = normalizeUtcIso(atUtc);
    const updated: QueuedJobState = {
      ...current,
      result: {
        ...current.result,
        status: "running",
        logs: appendLog(current.result.logs, {
          level: "info",
          event: "job.running",
          message: "Job execution started",
          atUtc: normalized
        })
      },
      lastUpdatedUtc: normalized
    };

    this.#states.set(jobId, updated);
    return updated;
  }

  markFinished(input: {
    jobId: string;
    status: Extract<JobStatus, "completed" | "failed">;
    output: Record<string, JsonValue>;
    atUtc: string;
    message: string;
    event: string;
    level?: "info" | "warn" | "error";
  }): QueuedJobState | null {
    const current = this.#states.get(input.jobId);
    if (!current) {
      return null;
    }

    const normalized = normalizeUtcIso(input.atUtc);
    const updated: QueuedJobState = {
      ...current,
      result: {
        ...current.result,
        status: input.status,
        output: input.output,
        logs: appendLog(current.result.logs, {
          level: input.level ?? (input.status === "completed" ? "info" : "error"),
          event: input.event,
          message: input.message,
          atUtc: normalized
        }),
        finishedAtUtc: normalized
      },
      lastUpdatedUtc: normalized
    };

    this.#states.set(input.jobId, updated);
    return updated;
  }

  markSkipped(jobId: string, atUtc: string, message: string): QueuedJobState | null {
    const current = this.#states.get(jobId);
    if (!current) {
      return null;
    }

    const normalized = normalizeUtcIso(atUtc);
    const updated: QueuedJobState = {
      ...current,
      result: {
        ...current.result,
        logs: appendLog(current.result.logs, {
          level: "warn",
          event: "job.run.skipped",
          message,
          atUtc: normalized
        })
      },
      lastUpdatedUtc: normalized
    };
    this.#states.set(jobId, updated);
    return updated;
  }

  snapshot(): QueueSnapshot {
    const values = [...this.#states.values()];
    const counts: QueueSnapshot = {
      queued: 0,
      running: 0,
      completed: 0,
      failed: 0,
      total: values.length
    };

    for (const item of values) {
      counts[item.result.status] += 1;
    }

    return counts;
  }
}
