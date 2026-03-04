import path from "node:path"
import { parseCliArgs, flagString, flagBoolean, flagNumber } from "../../lib/pitch-engine-tooling/args.mjs"
import { createLogger } from "../../lib/pitch-engine-tooling/logger.mjs"
import { resolvePitchArtifactsRoot } from "../../lib/pitch-engine-tooling/paths.mjs"

export function parseCommonFlags(argv = process.argv.slice(2)) {
  const parsed = parseCliArgs(argv)
  const programId = flagString(parsed.flags, ["programId", "program", "p"], "hitech-pitch")
  const runId = flagString(parsed.flags, ["runId", "run"])
  const sequenceId = flagString(parsed.flags, ["sequenceId", "sequence"])
  const sceneId = flagString(parsed.flags, ["sceneId", "scene"])
  const actor = flagString(parsed.flags, ["actor"], process.env.USERNAME ?? "codex")
  const note = flagString(parsed.flags, ["append", "note"])
  const reason = flagString(parsed.flags, ["reason"])
  const smoke = flagBoolean(parsed.flags, ["smoke"], false)
  const full = flagBoolean(parsed.flags, ["full"], false)
  const updateBaseline = flagBoolean(parsed.flags, ["update-baseline", "updateBaseline"], false)
  const keepLast = flagNumber(parsed.flags, ["keep", "keepLast"], undefined)
  const forceLite = flagBoolean(parsed.flags, ["lite", "force-lite"], false)

  return {
    parsed,
    programId,
    runId,
    sequenceId,
    sceneId,
    actor,
    note,
    reason,
    smoke,
    full,
    updateBaseline,
    keepLast,
    forceLite
  }
}

export function resolveMode(commonFlags) {
  if (commonFlags.smoke) {
    return "smoke"
  }
  if (commonFlags.full) {
    return "full"
  }
  if (commonFlags.updateBaseline) {
    return "update"
  }
  return "full"
}

export function makeLogger(prefix) {
  const logFile = path.join(resolvePitchArtifactsRoot(), "cli.log")
  return createLogger({ prefix, logFile })
}

export function printJson(value) {
  console.log(JSON.stringify(value, null, 2))
}

export function failAndExit(error, logger) {
  const message = error instanceof Error ? error.message : String(error)
  if (logger) {
    logger.fail(message)
  } else {
    console.error(message)
  }
  process.exitCode = 1
}
