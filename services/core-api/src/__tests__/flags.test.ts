import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { FEATURE_FLAGS_DEFAULTS, validateJobRequest } from "../contracts.js";

describe("validateJobRequest", () => {
  it("normalizes and accepts valid request payload", () => {
    const parsed = validateJobRequest({
      jobId: "job-42",
      kind: "summarize_text",
      input: {
        text: "hello world",
        priority: 2
      },
      requestedAtUtc: "2026-01-01T00:00:00Z"
    });

    assert.equal(parsed.ok, true);
    assert.ok(parsed.value);
    assert.equal(parsed.value?.jobId, "job-42");
    assert.deepEqual(parsed.value?.flags, FEATURE_FLAGS_DEFAULTS);
  });

  it("rejects invalid request payload with explicit issues", () => {
    const parsed = validateJobRequest({
      jobId: "",
      kind: "unknown",
      input: "not-object",
      requestedAtUtc: "nope"
    });

    assert.equal(parsed.ok, false);
    assert.ok(parsed.issues.length >= 3);
    assert.equal(parsed.issues.some((item) => item.path === "jobId"), true);
  });
});
