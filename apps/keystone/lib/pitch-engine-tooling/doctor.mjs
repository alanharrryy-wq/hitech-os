import net from "node:net"
import os from "node:os"
import path from "node:path"
import { DOCTOR_LOG_FILE, PLAYWRIGHT_CLI_TIMEOUT_MS, PLAYWRIGHT_PACKAGE_SPEC } from "./constants.mjs"
import { commandExists, runCommand } from "./exec.mjs"
import { ensureWritableDirectory, pathExists } from "./fs-utils.mjs"
import { createLogger } from "./logger.mjs"
import { resolvePitchArtifactsRoot, resolveRepoArtifactsRoot } from "./paths.mjs"

function parseNodeMajor(versionString) {
  const raw = versionString.startsWith("v") ? versionString.slice(1) : versionString
  const major = Number.parseInt(raw.split(".")[0], 10)
  return Number.isFinite(major) ? major : 0
}

async function isPortOpen(port) {
  return new Promise((resolve) => {
    const server = net.createServer()

    server.once("error", () => {
      resolve(false)
    })

    server.once("listening", () => {
      server.close(() => resolve(true))
    })

    server.listen(port, "127.0.0.1")
  })
}

async function checkPlaywrightCli(cwd) {
  const command = await commandExists("npx", cwd)
  if (!command) {
    return {
      ok: false,
      details: "npx command is not available"
    }
  }

  const result = await runCommand("npx", ["-y", PLAYWRIGHT_PACKAGE_SPEC, "--version"], {
    cwd,
    captureOutput: true,
    timeoutMs: PLAYWRIGHT_CLI_TIMEOUT_MS
  })

  if (result.exitCode !== 0) {
    return {
      ok: false,
      details: result.stderr || "Failed to invoke playwright CLI"
    }
  }

  return {
    ok: true,
    details: (result.stdout || "").trim()
  }
}

async function ensurePlaywrightBrowser(cwd) {
  const result = await runCommand(
    "npx",
    ["-y", PLAYWRIGHT_PACKAGE_SPEC, "install", "chromium"],
    {
      cwd,
      captureOutput: true,
      timeoutMs: PLAYWRIGHT_CLI_TIMEOUT_MS
    }
  )

  if (result.exitCode !== 0) {
    return {
      ok: false,
      details: result.stderr || "Failed to install Chromium browser"
    }
  }

  return {
    ok: true,
    details: "Chromium browser ready"
  }
}

export async function runDoctor(options = {}) {
  const cwd = options.cwd ?? process.cwd()
  const logger = createLogger({
    prefix: options.prefix ?? "doctor",
    logFile: options.logFile ?? path.join(resolvePitchArtifactsRoot(), DOCTOR_LOG_FILE)
  })

  const checks = []

  const nodeMajor = parseNodeMajor(process.version)
  checks.push({
    id: "node",
    ok: nodeMajor >= 20,
    details: `Node ${process.version}`
  })

  checks.push({
    id: "platform",
    ok: process.platform === "win32",
    details: `Platform ${process.platform}`
  })

  const hasPnpm = await commandExists("pnpm", cwd)
  checks.push({
    id: "pnpm",
    ok: hasPnpm,
    details: hasPnpm ? "pnpm available" : "pnpm not available"
  })

  const playwrightCli = await checkPlaywrightCli(cwd)
  checks.push({
    id: "playwright-cli",
    ok: playwrightCli.ok,
    details: playwrightCli.details
  })

  if (playwrightCli.ok && options.skipBrowserInstall !== true) {
    const browser = await ensurePlaywrightBrowser(cwd)
    checks.push({
      id: "playwright-browser",
      ok: browser.ok,
      details: browser.details
    })
  } else {
    checks.push({
      id: "playwright-browser",
      ok: false,
      details: "Skipped because playwright CLI is unavailable"
    })
  }

  const artifactsRoot = resolveRepoArtifactsRoot()
  const artifactsRootExists = await pathExists(artifactsRoot)
  checks.push({
    id: "artifacts-root",
    ok: artifactsRootExists,
    details: artifactsRoot
  })

  try {
    await ensureWritableDirectory(resolvePitchArtifactsRoot())
    checks.push({
      id: "artifacts-write",
      ok: true,
      details: resolvePitchArtifactsRoot()
    })
  } catch (error) {
    checks.push({
      id: "artifacts-write",
      ok: false,
      details: error instanceof Error ? error.message : String(error)
    })
  }

  const portFree = await isPortOpen(3100)
  checks.push({
    id: "port-3100",
    ok: true,
    details: portFree ? "Port 3100 available" : "Port 3100 already in use (acceptable if Next dev is running)"
  })

  checks.push({
    id: "memory",
    ok: true,
    details: `totalMemGb=${(os.totalmem() / (1024 ** 3)).toFixed(2)} cpus=${os.cpus().length}`
  })

  const failed = checks.filter((entry) => !entry.ok)

  for (const check of checks) {
    if (check.ok) {
      logger.pass(`${check.id}: ${check.details}`)
    } else {
      logger.fail(`${check.id}: ${check.details}`)
    }
  }

  return {
    ok: failed.length === 0,
    checks,
    failedCount: failed.length,
    generatedAtUtc: new Date().toISOString()
  }
}
