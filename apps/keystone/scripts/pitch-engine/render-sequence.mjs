#!/usr/bin/env node
import { renderSingleSequence } from "../../lib/pitch-engine-tooling/renderer.mjs"
import { parseCommonFlags, resolveMode, makeLogger, printJson, failAndExit } from "./_common.mjs"

async function main() {
  const logger = makeLogger("pitch:render:sequence")
  const flags = parseCommonFlags()
  const mode = resolveMode(flags)

  if (!flags.sequenceId) {
    throw new Error("Missing --sequenceId for sequence render.")
  }

  logger.info("Rendering single sequence", {
    programId: flags.programId,
    sequenceId: flags.sequenceId,
    mode
  })

  const result = await renderSingleSequence({
    programId: flags.programId,
    runId: flags.runId,
    sequenceId: flags.sequenceId,
    mode,
    keepLast: flags.keepLast,
    forceLite: flags.forceLite,
    allowDoctorFail: true,
    repoRoot: process.cwd()
  })

  printJson({
    ok: true,
    command: "keystone:pitch:render:sequence",
    programId: result.programId,
    runId: result.runId,
    sequence: result.selectedSequence,
    runDir: result.runDir
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:render:sequence"))
})
