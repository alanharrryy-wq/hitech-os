#!/usr/bin/env node
import { appendSceneNote } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { parseSceneFlags, sceneLogger, outputJson, failScene } from "./_common.mjs"

async function main() {
  const flags = parseSceneFlags()
  if (!flags.sceneId || !flags.runId || !flags.note) {
    throw new Error("Missing --sceneId, --runId, or --append")
  }

  const result = await appendSceneNote({
    sceneId: flags.sceneId,
    runId: flags.runId,
    actor: flags.actor,
    note: flags.note
  })

  outputJson({ ok: true, command: "keystone:scene:notes", result })
}

main().catch((error) => failScene(error, sceneLogger("scene:notes")))
