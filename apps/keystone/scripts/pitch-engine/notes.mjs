#!/usr/bin/env node
import { appendSequenceNotes } from "../../lib/pitch-engine-tooling/triage.mjs"
import { parseCommonFlags, failAndExit, makeLogger, printJson } from "./_common.mjs"
import { resolveLatestRunId } from "./_triage-common.mjs"

async function main() {
  const flags = parseCommonFlags()
  if (!flags.sequenceId) {
    throw new Error("Missing --sequenceId")
  }
  if (!flags.note) {
    throw new Error("Missing --append note text")
  }

  const runId = flags.runId ?? (await resolveLatestRunId(flags.programId))
  if (!runId) {
    throw new Error("No runId provided and no latest run found.")
  }

  const result = await appendSequenceNotes({
    programId: flags.programId,
    runId,
    sequenceId: flags.sequenceId,
    actor: flags.actor,
    note: flags.note
  })

  printJson({ ok: true, command: "keystone:pitch:notes", result })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:notes"))
})
