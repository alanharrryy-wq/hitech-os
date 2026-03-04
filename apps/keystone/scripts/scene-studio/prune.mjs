#!/usr/bin/env node
import { pruneSceneRuns } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { parseSceneFlags, sceneLogger, outputJson, failScene } from "./_common.mjs"

async function main() {
  const flags = parseSceneFlags()
  const result = await pruneSceneRuns({
    keepLast: flags.keepLast
  })

  outputJson({ ok: true, command: "keystone:scene:prune", result })
}

main().catch((error) => failScene(error, sceneLogger("scene:prune")))
