#!/usr/bin/env node
import { runCommand } from "../../lib/pitch-engine-tooling/exec.mjs"
import { parseCommonFlags, makeLogger, failAndExit, printJson } from "./_common.mjs"

async function main() {
  const logger = makeLogger("pitch:onebutton")
  const flags = parseCommonFlags()

  logger.info("Starting one-button flow", {
    programId: flags.programId
  })

  const steps = [
    {
      id: "doctor",
      command: "pnpm",
      args: ["--filter", "@hitech/keystone", "run", "keystone:pitch:doctor"]
    },
    {
      id: "render",
      command: "pnpm",
      args: [
        "--filter",
        "@hitech/keystone",
        "run",
        "keystone:pitch:render",
        "--",
        `--programId=${flags.programId}`,
        "--smoke"
      ]
    },
    {
      id: "dod",
      command: "pnpm",
      args: ["--filter", "@hitech/keystone", "run", "keystone:pitch:dod", "--", "--limited"]
    }
  ]

  const results = []

  for (const step of steps) {
    logger.info(`Running step ${step.id}`)
    const result = await runCommand(step.command, step.args, {
      cwd: process.cwd(),
      captureOutput: true,
      timeoutMs: 15 * 60 * 1000
    })

    results.push({
      id: step.id,
      exitCode: result.exitCode,
      durationMs: result.durationMs,
      stdout: result.stdout,
      stderr: result.stderr
    })

    if (result.exitCode !== 0) {
      logger.fail(`Step failed: ${step.id}`)
      console.log(JSON.stringify({ ok: false, step: step.id, results }, null, 2))
      process.exitCode = 1
      return
    }
  }

  printJson({
    ok: true,
    command: "keystone:pitch:onebutton",
    results
  })
}

main().catch((error) => {
  failAndExit(error, makeLogger("pitch:onebutton"))
})
