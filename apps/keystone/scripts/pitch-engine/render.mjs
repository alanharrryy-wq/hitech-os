#!/usr/bin/env node
import { renderProgram } from "../../lib/pitch-engine-tooling/renderer.mjs"
import { writePitchIndexFiles } from "../../lib/pitch-engine-tooling/indexer.mjs"
import { parseCommonFlags, resolveMode, makeLogger, printJson, failAndExit } from "./_common.mjs"

async function main() {
  const logger = makeLogger("pitch:render")
  const flags = parseCommonFlags()
  const mode = resolveMode(flags)

  logger.info("Rendering program", {
    programId: flags.programId,
    runId: flags.runId,
    mode,
    updateBaseline: flags.updateBaseline
  })

  const result = await renderProgram({
    programId: flags.programId,
    runId: flags.runId,
    mode,
    keepLast: flags.keepLast,
    forceLite: flags.forceLite,
    allowDoctorFail: true,
    repoRoot: process.cwd()
  })

  await writePitchIndexFiles()

  printJson({
    ok: true,
    command: "keystone:pitch:render",
    programId: result.programId,
    runId: result.runId,
    mode,
    capture: result.capture,
    retention: result.retention.counts,
    runDir: result.runDir
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:render"))
})
