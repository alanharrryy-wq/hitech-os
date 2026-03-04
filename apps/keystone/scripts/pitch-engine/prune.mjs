#!/usr/bin/env node
import { pruneProgramRuns } from "../../lib/pitch-engine-tooling/retention.mjs"
import { parseCommonFlags, failAndExit, makeLogger, printJson } from "./_common.mjs"

async function main() {
  const flags = parseCommonFlags()
  const result = await pruneProgramRuns(flags.programId, {
    keepLast: flags.keepLast
  })

  printJson({
    ok: true,
    command: "keystone:pitch:prune",
    result
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:prune"))
})
