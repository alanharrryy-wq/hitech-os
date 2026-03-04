#!/usr/bin/env node
import { pinSceneRun } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { parseSceneFlags, sceneLogger, outputJson, failScene } from "./_common.mjs"

async function main() {
  const flags = parseSceneFlags()
  if (!flags.sceneId || !flags.runId) {
    throw new Error("Missing --sceneId or --runId")
  }

  const result = await pinSceneRun({
    sceneId: flags.sceneId,
    runId: flags.runId,
    actor: flags.actor
  })

  outputJson({ ok: true, command: "keystone:scene:pin", result })
}

main().catch((error) => failScene(error, sceneLogger("scene:pin")))
