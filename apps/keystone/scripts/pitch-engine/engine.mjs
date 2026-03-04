#!/usr/bin/env node
import { runCommand } from "../../lib/pitch-engine-tooling/exec.mjs"

async function main() {
  const result = await runCommand(
    "pnpm",
    ["--filter", "@hitech/keystone", "run", "keystone:pitch:onebutton"],
    {
      cwd: process.cwd(),
      captureOutput: true,
      timeoutMs: 20 * 60 * 1000
    }
  )

  if (result.stdout) {
    process.stdout.write(result.stdout)
  }

  if (result.stderr) {
    process.stderr.write(result.stderr)
  }

  if (result.exitCode !== 0) {
    process.exitCode = result.exitCode
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exitCode = 1
})
