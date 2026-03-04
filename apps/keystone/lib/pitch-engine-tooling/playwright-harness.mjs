import path from "node:path"
import { PLAYWRIGHT_CLI_TIMEOUT_MS, PLAYWRIGHT_PACKAGE_SPEC } from "./constants.mjs"
import { runCommand } from "./exec.mjs"
import { pathExists, readJsonIfExists, writeJsonFile } from "./fs-utils.mjs"
import { writePlaceholderPng } from "./image-utils.mjs"

const SPEC_FILE = "apps/keystone/scripts/pitch-engine/playwright-capture.spec.mjs"

export async function runPlaywrightCapture(job, options = {}) {
  const cwd = options.cwd ?? process.cwd()

  const runPath = path.join(job.tempDir, `capture-job-${job.runId}.json`)
  const resultPath = path.join(job.tempDir, `capture-result-${job.runId}.json`)

  await writeJsonFile(runPath, {
    ...job,
    resultPath
  })

  const env = {
    ...process.env,
    PITCH_ENGINE_CAPTURE_JOB_PATH: runPath,
    PITCH_ENGINE_CAPTURE_RESULT_PATH: resultPath
  }

  const args = [
    "-y",
    PLAYWRIGHT_PACKAGE_SPEC,
    "test",
    SPEC_FILE,
    "--workers=1",
    "--reporter=line",
    "--timeout=120000"
  ]

  const commandResult = await runCommand("npx", args, {
    cwd,
    env,
    captureOutput: true,
    timeoutMs: PLAYWRIGHT_CLI_TIMEOUT_MS
  })

  const resultExists = await pathExists(resultPath)
  const payload = resultExists
    ? await readJsonIfExists(resultPath, {
        captures: [],
        warnings: ["Missing result payload."],
        strategy: "playwright"
      })
    : {
        captures: [],
        warnings: [
          "Playwright capture did not produce a result payload.",
          commandResult.stderr || commandResult.stdout || "No command output captured."
        ],
        strategy: "fallback"
      }

  if (commandResult.exitCode !== 0) {
    payload.warnings = [
      ...(payload.warnings ?? []),
      `Playwright exit code ${commandResult.exitCode}`,
      commandResult.stderr || "No stderr output"
    ]
    payload.strategy = "fallback"
  }

  return {
    ok: commandResult.exitCode === 0,
    commandResult,
    payload,
    jobPath: runPath,
    resultPath
  }
}

export async function fallbackCapture(job) {
  const captures = []

  for (const task of job.tasks) {
    await writePlaceholderPng(task.outputPath)
    captures.push({
      sequenceId: task.sequenceId,
      sceneId: task.sceneId,
      route: task.route,
      tMs: task.tMs,
      outputPath: task.outputPath,
      marker: task.marker ?? null,
      sceneReadyDetected: false,
      strategy: "placeholder"
    })
  }

  return {
    captures,
    warnings: [
      "Playwright unavailable or failed; deterministic placeholder PNGs were generated.",
      "Install Chromium with `npx -y playwright@1.51.1 install chromium` for live captures."
    ],
    strategy: "placeholder"
  }
}
