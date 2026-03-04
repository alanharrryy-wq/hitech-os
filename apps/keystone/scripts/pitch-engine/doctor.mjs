#!/usr/bin/env node
import path from "node:path"
import { runDoctor } from "../../lib/pitch-engine-tooling/doctor.mjs"
import { resolvePitchArtifactsRoot } from "../../lib/pitch-engine-tooling/paths.mjs"
import { parseCliArgs, flagBoolean } from "../../lib/pitch-engine-tooling/args.mjs"

async function main() {
  const parsed = parseCliArgs(process.argv.slice(2))
  const skipBrowserInstall = flagBoolean(parsed.flags, ["skip-browser-install"], false)

  const result = await runDoctor({
    cwd: process.cwd(),
    skipBrowserInstall,
    prefix: "pitch-doctor",
    logFile: path.join(resolvePitchArtifactsRoot(), "doctor-cli.log")
  })

  console.log(JSON.stringify(result, null, 2))

  if (!result.ok) {
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error))
  process.exitCode = 1
})
