import { describe, expect, it } from "vitest"
import { appendSequenceNotes, rejectSequence } from "../../lib/pitch-engine-tooling/triage.mjs"
import { ensureDir, pathExists, readJsonIfExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolveSequenceDecisionPath, resolveSequenceDir, resolveSequenceNotesPath } from "../../lib/pitch-engine-tooling/paths.mjs"

describe("triage", () => {
  it("writes sequence notes", async () => {
    const programId = "triage-test"
    const runId = "20260304_020202_BBBB"
    const sequenceId = "01-double-engine"

    await ensureDir(resolveSequenceDir(programId, runId, sequenceId))

    const result = await appendSequenceNotes({
      programId,
      runId,
      sequenceId,
      actor: "tester",
      note: "deterministic note"
    })

    expect(result.appended).toBe(true)
    expect(await pathExists(resolveSequenceNotesPath(programId, runId, sequenceId))).toBe(true)
  })

  it("writes rejected decision", async () => {
    const programId = "triage-test"
    const runId = "20260304_020202_BBBB"
    const sequenceId = "01-double-engine"

    await ensureDir(resolveSequenceDir(programId, runId, sequenceId))

    const result = await rejectSequence({
      programId,
      runId,
      sequenceId,
      actor: "tester",
      reason: "Mismatch"
    })

    expect(result.status).toBe("rejected")

    const decision = await readJsonIfExists(resolveSequenceDecisionPath(programId, runId, sequenceId), null)
    expect(decision.current.status).toBe("rejected")
  })
})
