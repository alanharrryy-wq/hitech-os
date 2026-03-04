#!/usr/bin/env node
import { acceptSequenceBaseline } from "../../lib/pitch-engine-tooling/triage.mjs"
import { parseCommonFlags, failAndExit, makeLogger, printJson } from "./_common.mjs"
import { resolveLatestRunId } from "./_triage-common.mjs"

async function main() {
  const flags = parseCommonFlags()
  if (!flags.sequenceId) {
    throw new Error("Missing --sequenceId")
  }

  const runId = flags.runId ?? (await resolveLatestRunId(flags.programId))
  if (!runId) {
    throw new Error("No runId provided and no latest run found.")
  }

  const result = await acceptSequenceBaseline({
    programId: flags.programId,
    runId,
    sequenceId: flags.sequenceId,
    actor: flags.actor,
    reason: flags.reason
  })

  printJson({ ok: true, command: "keystone:pitch:accept", result })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:accept"))
})
