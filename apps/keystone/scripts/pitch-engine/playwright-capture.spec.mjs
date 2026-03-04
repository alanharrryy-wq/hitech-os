import fs from "node:fs/promises"
import path from "node:path"
import { test } from "@playwright/test"

const jobPath = process.env.PITCH_ENGINE_CAPTURE_JOB_PATH
const resultPath = process.env.PITCH_ENGINE_CAPTURE_RESULT_PATH

function failEarly(message) {
  throw new Error(`[playwright-capture] ${message}`)
}

test("deterministic keystone capture", async ({ browser }) => {
  if (!jobPath) {
    failEarly("Missing PITCH_ENGINE_CAPTURE_JOB_PATH")
  }

  if (!resultPath) {
    failEarly("Missing PITCH_ENGINE_CAPTURE_RESULT_PATH")
  }

  const payloadRaw = await fs.readFile(jobPath, "utf8")
  const job = JSON.parse(payloadRaw)

  const viewport = job.viewport ?? { width: 1440, height: 900 }
  const profile = job.profile ?? {
    frameSettleMs: 120,
    sceneReadyTimeoutMs: 2000,
    postGotoWaitMs: 50
  }
  const navigationTimeoutMs = Number(job.navigationTimeoutMs ?? 8000)

  const warnings = []
  const captures = []

  const context = await browser.newContext({
    viewport,
    reducedMotion: "reduce",
    colorScheme: "light",
    locale: "en-US",
    timezoneId: "UTC",
    deviceScaleFactor: 1
  })

  const page = await context.newPage()

  await page.addInitScript(() => {
    const style = document.createElement("style")
    style.id = "pitch-engine-deterministic-style"
    style.textContent = [
      "*{animation:none !important;transition:none !important;}",
      "*::before,*::after{animation:none !important;transition:none !important;}",
      "html{scroll-behavior:auto !important;}"
    ].join("")
    document.documentElement.appendChild(style)

    document.documentElement.setAttribute("data-pe-reduced-motion", "1")
    document.documentElement.setAttribute("data-pe-deterministic", "1")
  })

  for (const task of job.tasks ?? []) {
    const taskUrl = new URL(task.route, "http://127.0.0.1:3100")
    taskUrl.searchParams.set("peReducedMotion", "1")
    taskUrl.searchParams.set("peDeterministic", "1")
    taskUrl.searchParams.set("peTime", String(task.tMs))
    taskUrl.searchParams.set("peProfile", String(profile.name ?? "full"))

    const captureRecord = {
      programId: task.programId,
      runId: task.runId,
      sequenceId: task.sequenceId,
      sceneId: task.sceneId,
      route: task.route,
      tMs: task.tMs,
      marker: task.marker ?? null,
      outputPath: task.outputPath,
      markerOutputPath: task.markerOutputPath ?? null,
      sceneReadyDetected: false,
      strategy: "playwright"
    }

    try {
      await page.goto(taskUrl.toString(), {
        waitUntil: "domcontentloaded",
        timeout: navigationTimeoutMs
      })

      try {
        await page.waitForSelector('[data-scene-ready="1"]', {
          timeout: profile.sceneReadyTimeoutMs
        })
        captureRecord.sceneReadyDetected = true
      } catch {
        warnings.push(`Scene ready signal missing for ${task.sequenceId} at ${task.tMs}ms.`)
      }

      await page.waitForTimeout(Number(profile.postGotoWaitMs ?? 50))

      await page.evaluate((timeMs) => {
        document.documentElement.setAttribute("data-pe-time-ms", String(timeMs))
        document.body?.setAttribute("data-pe-time-ms", String(timeMs))
        const event = new CustomEvent("pitch-engine:seek", {
          detail: {
            tMs: timeMs,
            deterministic: true
          }
        })
        window.dispatchEvent(event)
      }, task.tMs)

      await page.waitForTimeout(Number(profile.frameSettleMs ?? 120))

      await fs.mkdir(path.dirname(task.outputPath), { recursive: true })
      await page.screenshot({
        path: task.outputPath,
        fullPage: false,
        animations: "disabled"
      })

      if (task.markerOutputPath) {
        await fs.copyFile(task.outputPath, task.markerOutputPath)
      }

      captures.push(captureRecord)
    } catch (error) {
      warnings.push(
        `Capture failed for ${task.sequenceId} at ${task.tMs}ms: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  await context.close()

  const resultPayload = {
    generatedAtUtc: new Date().toISOString(),
    captures,
    warnings,
    strategy: "playwright",
    captureCount: captures.length
  }

  await fs.mkdir(path.dirname(resultPath), { recursive: true })
  await fs.writeFile(resultPath, JSON.stringify(resultPayload, null, 2) + "\n", "utf8")
})
