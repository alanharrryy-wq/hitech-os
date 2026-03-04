#!/usr/bin/env node
import fs from "node:fs/promises"
import path from "node:path"
import {
  DOD_CHECK_STATUS,
  DOD_CHECKLIST_FILE,
  PITCH_ARTIFACT_ROOT,
  SAFE_AUTOFIX_IDS
} from "../../../../apps/keystone/lib/pitch-engine-tooling/constants.mjs"
import { parseCliArgs, flagBoolean } from "../../../../apps/keystone/lib/pitch-engine-tooling/args.mjs"
import {
  pathExists,
  readJsonFile,
  writeJsonFile,
  writeTextFile
} from "../../../../apps/keystone/lib/pitch-engine-tooling/fs-utils.mjs"
import { runDodCheck } from "./checks.mjs"
import { runAutofixRegenerateIndexes } from "./autofix/regenerate_indexes.mjs"
import { runAutofixNormalizeArtifactsIndex } from "./autofix/normalize_artifacts_index.mjs"
import { runAutofixNormalizeNames } from "./autofix/normalize_names.mjs"
import { runAutofixRegenerateRouteDiscovery } from "./autofix/regenerate_route_discovery.mjs"

function resolveAutofixHandler(autofixId) {
  switch (autofixId) {
    case SAFE_AUTOFIX_IDS.regenerateIndexes:
      return () => runAutofixRegenerateIndexes()
    case SAFE_AUTOFIX_IDS.normalizeArtifactsIndex:
      return () => runAutofixNormalizeArtifactsIndex()
    case SAFE_AUTOFIX_IDS.normalizeNames:
      return () => runAutofixNormalizeNames()
    case SAFE_AUTOFIX_IDS.regenRouteDiscoveryOutputs:
      return () => runAutofixRegenerateRouteDiscovery(process.cwd())
    default:
      return null
  }
}

function toCheckLine(result) {
  return `[${result.status}] ${result.id} :: ${result.detail}`
}

function summarize(results) {
  const counts = {
    PASS: 0,
    FAIL: 0,
    WARN: 0,
    SKIP: 0
  }

  for (const result of results) {
    if (!Object.prototype.hasOwnProperty.call(counts, result.status)) {
      continue
    }
    counts[result.status] += 1
  }

  return counts
}

function filterChecksByMode(checklist, options) {
  if (!options.limited) {
    return checklist.checks
  }

  return checklist.checks.filter((check) => check.ownership === "B_tooling")
}

async function loadChecklist(repoRoot) {
  const absolutePath = path.join(repoRoot, DOD_CHECKLIST_FILE)
  if (!(await pathExists(absolutePath))) {
    throw new Error(`Missing DoD checklist: ${absolutePath}`)
  }
  return readJsonFile(absolutePath)
}

async function resolveRepoRoot(startDir) {
  const visited = new Set()
  let current = path.resolve(startDir)

  while (!visited.has(current)) {
    visited.add(current)
    const contractPath = path.join(current, "docs/CONTRACT.md")
    const keystonePath = path.join(current, "apps/keystone/package.json")
    const dodPath = path.join(current, DOD_CHECKLIST_FILE)

    if ((await pathExists(contractPath)) && (await pathExists(keystonePath)) && (await pathExists(dodPath))) {
      return current
    }

    const parent = path.dirname(current)
    if (parent === current) {
      break
    }
    current = parent
  }

  throw new Error(
    `Unable to resolve repo root from cwd=${startDir}. Expected docs/CONTRACT.md and apps/keystone/package.json.`
  )
}

async function runChecks(checks, context, options) {
  const results = []
  const autofixLog = []

  for (const check of checks) {
    const result = await runDodCheck(check, context)
    results.push(result)

    const needsAutofix =
      options.autofix &&
      result.status === DOD_CHECK_STATUS.fail &&
      typeof check.autofix === "string" &&
      check.autofix.length > 0

    if (!needsAutofix) {
      continue
    }

    const handler = resolveAutofixHandler(check.autofix)
    if (!handler) {
      autofixLog.push({
        id: check.autofix,
        ok: false,
        detail: "No handler registered"
      })
      continue
    }

    const fixResult = await handler()
    autofixLog.push(fixResult)

    if (fixResult.ok) {
      const rerun = await runDodCheck(check, context)
      rerun.detail = `${rerun.detail} (after autofix ${check.autofix})`
      results[results.length - 1] = rerun
    }
  }

  return {
    results,
    autofixLog
  }
}

async function writeResultsArtifacts(repoRoot, payload) {
  const outputPath = path.join(PITCH_ARTIFACT_ROOT, "last_dod.json")
  await writeJsonFile(outputPath, payload)

  const summaryPath = path.join(repoRoot, "tools/hos/quality/dod/last_dod_summary.md")
  const lines = [
    "# Last DoD Summary",
    "",
    `Generated: ${payload.generatedAtUtc}`,
    `Mode: ${payload.mode}`,
    "",
    "## Counts",
    `- PASS: ${payload.counts.PASS}`,
    `- FAIL: ${payload.counts.FAIL}`,
    `- WARN: ${payload.counts.WARN}`,
    `- SKIP: ${payload.counts.SKIP}`,
    "",
    "## Checks",
    ...payload.results.map((entry) => `- ${toCheckLine(entry)}`),
    ""
  ]

  await writeTextFile(summaryPath, lines.join("\n") + "\n")

  return {
    outputPath,
    summaryPath
  }
}

async function main() {
  const repoRoot = await resolveRepoRoot(process.cwd())
  const parsed = parseCliArgs(process.argv.slice(2))

  const options = {
    limited: flagBoolean(parsed.flags, ["limited"], false),
    autofix: flagBoolean(parsed.flags, ["autofix"], true),
    skipTests: flagBoolean(parsed.flags, ["skip-tests"], false)
  }

  const checklist = await loadChecklist(repoRoot)
  const selectedChecks = filterChecksByMode(checklist, options)

  const context = {
    repoRoot,
    options
  }

  const { results, autofixLog } = await runChecks(selectedChecks, context, options)
  const counts = summarize(results)

  const payload = {
    generatedAtUtc: new Date().toISOString(),
    mode: options.limited ? "limited" : "full",
    checklistVersion: checklist.version,
    checklistName: checklist.name,
    counts,
    autofixEnabled: options.autofix,
    autofixLog,
    results
  }

  const artifacts = await writeResultsArtifacts(repoRoot, payload)

  for (const result of results) {
    console.log(toCheckLine(result))
  }

  console.log(
    JSON.stringify(
      {
        ok: counts.FAIL === 0,
        counts,
        output: artifacts.outputPath,
        summary: artifacts.summaryPath
      },
      null,
      2
    )
  )

  if (counts.FAIL > 0) {
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error))
  process.exitCode = 1
})
