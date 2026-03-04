#!/usr/bin/env node
import { renderSingleSequence } from "../../lib/pitch-engine-tooling/renderer.mjs"
import { parseCommonFlags, failAndExit, makeLogger, printJson } from "./_common.mjs"

async function main() {
  const flags = parseCommonFlags()

  if (!flags.sequenceId) {
    throw new Error("Missing --sequenceId")
  }

  const result = await renderSingleSequence({
    programId: flags.programId,
    runId: flags.runId,
    sequenceId: flags.sequenceId,
    mode: "smoke",
    allowDoctorFail: true,
    repoRoot: process.cwd()
  })

  printJson({
    ok: true,
    command: "keystone:pitch:rerun",
    runId: result.runId,
    sequence: result.selectedSequence
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:rerun"))
})
