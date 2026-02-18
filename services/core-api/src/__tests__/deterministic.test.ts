import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DeterministicJobQueue } from "../lib/jobQueue.ts";
import type { JobRequest } from "../contracts.ts";

const FLAGS_OFF = {
  enableAiExecution: false,
  enableCapabilitiesProxy: false,
  enableExperimentalUi: false,
  enableHealthDashboard: false
};

function buildRequest(jobId: string, requestedAtUtc: string): JobRequest {
  return {
    jobId,
    kind: "echo",
    input: {
      text: `payload-${jobId}`
    },
    requestedAtUtc,
    flags: FLAGS_OFF
  };
}

describe("DeterministicJobQueue", () => {
  it("orders queued jobs by requestedAtUtc and jobId deterministically", () => {
    const queue = new DeterministicJobQueue();
    queue.enqueue(buildRequest("job-b", "2026-01-02T10:00:00.000Z"));
    queue.enqueue(buildRequest("job-a", "2026-01-02T10:00:00.000Z"));
    queue.enqueue(buildRequest("job-c", "2026-01-01T10:00:00.000Z"));

    const ordered = queue.getOrdered().map((item) => item.request.jobId);
    assert.deepEqual(ordered, ["job-c", "job-a", "job-b"]);
  });

  it("is idempotent when enqueueing the same jobId", () => {
    const queue = new DeterministicJobQueue();
    const first = queue.enqueue(buildRequest("job-x", "2026-01-01T00:00:00.000Z"));
    const second = queue.enqueue(buildRequest("job-x", "2026-02-01T00:00:00.000Z"));

    assert.equal(first.enqueueSeq, second.enqueueSeq);
    assert.equal(queue.snapshot().total, 1);
    assert.equal(queue.snapshot().queued, 1);
  });
});
