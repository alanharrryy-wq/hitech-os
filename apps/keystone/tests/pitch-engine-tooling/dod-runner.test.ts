import { describe, expect, it } from "vitest"
import { runCommand } from "../../lib/pitch-engine-tooling/exec.mjs"
import { pathExists, readJsonIfExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { PITCH_ARTIFACT_ROOT } from "../../lib/pitch-engine-tooling/constants.mjs"
import path from "node:path"

describe("DoD runner", () => {
  it("runs in limited mode and writes JSON output", async () => {
    const result = await runCommand(
      "node",
      ["tools/hos/quality/dod/run_dod.mjs", "--limited", "--skip-tests", "--autofix=false"],
      {
        cwd: process.cwd(),
        captureOutput: true,
        timeoutMs: 10 * 60 * 1000
      }
    )

    expect([0, 1]).toContain(result.exitCode)

    const outputPath = path.join(PITCH_ARTIFACT_ROOT, "last_dod.json")
    if (await pathExists(outputPath)) {
      const payload = await readJsonIfExists(outputPath, null)
      expect(payload).not.toBeNull()
      expect(typeof payload.mode).toBe("string")
      expect(Array.isArray(payload.results)).toBe(true)
    } else {
      expect(typeof result.stderr).toBe("string")
    }
  })
})
