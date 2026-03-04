#!/usr/bin/env node
import { pinRun } from "../../lib/pitch-engine-tooling/retention.mjs"
import { parseCommonFlags, failAndExit, makeLogger, printJson } from "./_common.mjs"
import { resolveLatestRunId } from "./_triage-common.mjs"

async function main() {
  const flags = parseCommonFlags()
  const runId = flags.runId ?? (await resolveLatestRunId(flags.programId))

  if (!runId) {
    throw new Error("No runId provided and no latest run found.")
  }

  const result = await pinRun(flags.programId, runId, flags.actor)
  printJson({ ok: true, command: "keystone:pitch:pin", result })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:pin"))
})
