#!/usr/bin/env node
import { runCommand } from "../../lib/pitch-engine-tooling/exec.mjs"

async function main() {
  const steps = [
    {
      id: "scene-doctor",
      command: "pnpm",
      args: ["--filter", "@hitech/keystone", "run", "keystone:scene:doctor"]
    },
    {
      id: "scene-triage-index",
      command: "pnpm",
      args: ["--filter", "@hitech/keystone", "run", "keystone:scene:triage"]
    },
    {
      id: "scene-prune",
      command: "pnpm",
      args: ["--filter", "@hitech/keystone", "run", "keystone:scene:prune"]
    }
  ]

  const results = []

  for (const step of steps) {
    const result = await runCommand(step.command, step.args, {
      cwd: process.cwd(),
      captureOutput: true,
      timeoutMs: 15 * 60 * 1000
    })

    results.push({
      id: step.id,
      exitCode: result.exitCode,
      stdout: result.stdout,
      stderr: result.stderr,
      durationMs: result.durationMs
    })

    if (result.exitCode !== 0) {
      console.log(JSON.stringify({ ok: false, failedStep: step.id, results }, null, 2))
      process.exitCode = result.exitCode
      return
    }
  }

  console.log(JSON.stringify({ ok: true, command: "keystone:scene:onebutton", results }, null, 2))
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exitCode = 1
})
