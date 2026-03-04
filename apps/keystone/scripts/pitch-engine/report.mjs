#!/usr/bin/env node
import path from "node:path"
import { listDirectories, readJsonIfExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolveProgramDir, resolveProgramRunDir } from "../../lib/pitch-engine-tooling/paths.mjs"
import { parseCommonFlags, printJson, failAndExit, makeLogger } from "./_common.mjs"

async function resolveLatestRun(programId) {
  const runIds = await listDirectories(resolveProgramDir(programId))
  const candidates = runIds.filter((runId) => /^\d{8}_\d{6}_[A-Za-z0-9_-]+$/.test(runId))
  candidates.sort((a, b) => b.localeCompare(a))
  return candidates[0] ?? null
}

async function main() {
  const flags = parseCommonFlags()
  const runId = flags.runId ?? (await resolveLatestRun(flags.programId))

  if (!runId) {
    throw new Error(`No runs found for program ${flags.programId}`)
  }

  const runDir = resolveProgramRunDir(flags.programId, runId)
  const reportPath = path.join(runDir, "report.json")
  const report = await readJsonIfExists(reportPath, null)

  if (!report) {
    throw new Error(`Missing report.json for run ${runId}`)
  }

  printJson({
    ok: true,
    command: "keystone:pitch:report",
    programId: flags.programId,
    runId,
    report
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:report"))
})
