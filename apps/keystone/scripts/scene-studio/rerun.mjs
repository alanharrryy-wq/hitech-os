#!/usr/bin/env node
import { requestSceneRerun } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { parseSceneFlags, sceneLogger, outputJson, failScene } from "./_common.mjs"

async function main() {
  const flags = parseSceneFlags()
  if (!flags.sceneId) {
    throw new Error("Missing --sceneId")
  }

  const result = await requestSceneRerun({
    sceneId: flags.sceneId,
    actor: flags.actor,
    reason: flags.reason
  })

  outputJson({ ok: true, command: "keystone:scene:rerun", result })
}

main().catch((error) => failScene(error, sceneLogger("scene:rerun")))
