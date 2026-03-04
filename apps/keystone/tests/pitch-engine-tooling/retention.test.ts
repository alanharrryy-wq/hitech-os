import { describe, expect, it } from "vitest"
import { pinRun, pruneProgramRuns } from "../../lib/pitch-engine-tooling/retention.mjs"
import { ensureDir, pathExists, writeTextFile } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolveProgramRunDir, resolveRunPinMarkerPath } from "../../lib/pitch-engine-tooling/paths.mjs"

describe("retention", () => {
  it("pins run with marker", async () => {
    const programId = "retention-test"
    const runId = "20260304_010101_AAAA"
    await ensureDir(resolveProgramRunDir(programId, runId))
    const pin = await pinRun(programId, runId, "tester")
    expect(pin.pinned).toBe(true)
    expect(await pathExists(resolveRunPinMarkerPath(programId, runId))).toBe(true)
  })

  it("prunes unpinned runs while preserving recent runs", async () => {
    const programId = "retention-prune"
    const runs = [
      "20260304_000001_A001",
      "20260304_000002_A002",
      "20260304_000003_A003",
      "20260304_000004_A004"
    ]

    for (const runId of runs) {
      const dir = resolveProgramRunDir(programId, runId)
      await ensureDir(dir)
      await writeTextFile(`${dir}/probe.txt`, runId)
    }

    const result = await pruneProgramRuns(programId, {
      keepLast: 2
    })

    expect(result.counts.kept).toBeGreaterThanOrEqual(2)
    expect(result.counts.deleted).toBeGreaterThanOrEqual(1)
  })
})
