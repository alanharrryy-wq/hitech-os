#!/usr/bin/env node
import { sceneTriageOverview } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { parseSceneFlags, sceneLogger, outputJson, failScene } from "./_common.mjs"
import { resolveSceneIndexPath } from "../../lib/pitch-engine-tooling/paths.mjs"
import { runCommand } from "../../lib/pitch-engine-tooling/exec.mjs"

async function main() {
  const logger = sceneLogger("scene:triage")
  const flags = parseSceneFlags()
  const overview = await sceneTriageOverview()

  const indexHtml = resolveSceneIndexPath("index.html")

  if (flags.open && process.platform === "win32") {
    await runCommand("powershell", ["-NoProfile", "-Command", `Start-Process '${indexHtml.replace(/'/g, "''")}'`], {
      cwd: process.cwd(),
      captureOutput: true,
      timeoutMs: 20_000,
      shell: false
    })
    logger.info("Opened triage index in browser", { indexHtml })
  }

  outputJson({
    ok: true,
    command: "keystone:scene:triage",
    indexHtml,
    overview
  })
}

main().catch((error) => failScene(error, sceneLogger("scene:triage")))
