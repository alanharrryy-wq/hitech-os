#!/usr/bin/env node
import path from "node:path"
import { runDoctor } from "../../lib/pitch-engine-tooling/doctor.mjs"
import { sceneTriageOverview } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { resolveSceneArtifactsRoot } from "../../lib/pitch-engine-tooling/paths.mjs"

async function main() {
  const doctor = await runDoctor({
    cwd: process.cwd(),
    skipBrowserInstall: false,
    prefix: "scene-doctor",
    logFile: path.join(resolveSceneArtifactsRoot(), "doctor.log")
  })

  const overview = await sceneTriageOverview()

  const payload = {
    ok: doctor.ok,
    doctor,
    overview
  }

  console.log(JSON.stringify(payload, null, 2))

  if (!doctor.ok) {
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error))
  process.exitCode = 1
})
