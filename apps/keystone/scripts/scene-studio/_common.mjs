import { parseCliArgs, flagString, flagNumber, flagBoolean } from "../../lib/pitch-engine-tooling/args.mjs"
import { createLogger } from "../../lib/pitch-engine-tooling/logger.mjs"
import { resolveSceneArtifactsRoot } from "../../lib/pitch-engine-tooling/paths.mjs"
import path from "node:path"

export function parseSceneFlags(argv = process.argv.slice(2)) {
  const parsed = parseCliArgs(argv)
  return {
    parsed,
    sceneId: flagString(parsed.flags, ["sceneId", "scene"]),
    runId: flagString(parsed.flags, ["runId", "run"]),
    actor: flagString(parsed.flags, ["actor"], process.env.USERNAME ?? "codex"),
    note: flagString(parsed.flags, ["append", "note"]),
    reason: flagString(parsed.flags, ["reason"]),
    keepLast: flagNumber(parsed.flags, ["keep", "keepLast"], undefined),
    open: flagBoolean(parsed.flags, ["open"], false)
  }
}

export function sceneLogger(prefix) {
  return createLogger({
    prefix,
    logFile: path.join(resolveSceneArtifactsRoot(), "scene-cli.log")
  })
}

export function outputJson(value) {
  console.log(JSON.stringify(value, null, 2))
}

export function failScene(error, logger) {
  const message = error instanceof Error ? error.message : String(error)
  logger?.fail(message)
  console.error(message)
  process.exitCode = 1
}
