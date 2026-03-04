import { spawn } from "node:child_process"

function resolveCommand(command) {
  return command
}

function quoteForCmd(value) {
  const raw = String(value)
  if (raw.length === 0) {
    return "\"\""
  }

  if (!/[ \t"&()<>|^]/.test(raw)) {
    return raw
  }

  return `"${raw.replace(/"/g, '\\"')}"`
}

function killProcessTreeWindows(pid) {
  return new Promise((resolve) => {
    if (typeof pid !== "number" || Number.isNaN(pid)) {
      resolve(false)
      return
    }

    const killer = spawn("taskkill", ["/PID", String(pid), "/T", "/F"], {
      windowsHide: true,
      stdio: "ignore"
    })

    killer.on("close", () => {
      resolve(true)
    })

    killer.on("error", () => {
      resolve(false)
    })
  })
}

function killChildProcess(child) {
  if (!child || typeof child.pid !== "number") {
    return
  }

  if (process.platform === "win32") {
    void killProcessTreeWindows(child.pid)
    return
  }

  try {
    child.kill("SIGTERM")
  } catch {
    // no-op
  }
}

export function runCommand(command, args, options = {}) {
  const start = Date.now()
  return new Promise((resolve) => {
    let settled = false
    function settle(payload) {
      if (settled) {
        return
      }
      settled = true
      resolve(payload)
    }

    const resolvedCommand = resolveCommand(command)
    let spawnCommand = resolvedCommand
    let spawnArgs = [...args]
    let useShell = options.shell ?? false

    const needsCmdWrapper =
      process.platform === "win32" &&
      (resolvedCommand.toLowerCase() === "pnpm" || resolvedCommand.toLowerCase() === "npx") &&
      options.shell === undefined

    if (needsCmdWrapper) {
      spawnCommand = "cmd.exe"
      const cmdLine = [resolvedCommand, ...args.map((entry) => quoteForCmd(entry))].join(" ")
      spawnArgs = ["/d", "/s", "/c", cmdLine]
      useShell = false
    }

    const child = spawn(spawnCommand, spawnArgs, {
      cwd: options.cwd,
      env: options.env,
      shell: useShell,
      windowsHide: true,
      stdio: options.captureOutput ? ["ignore", "pipe", "pipe"] : "inherit"
    })

    let stdout = ""
    let stderr = ""

    if (options.captureOutput) {
      child.stdout?.on("data", (chunk) => {
        stdout += String(chunk)
      })

      child.stderr?.on("data", (chunk) => {
        stderr += String(chunk)
      })
    }

    const timeoutMs = options.timeoutMs
    let timedOut = false
    let timeoutHandle = null
    let hardTimeoutHandle = null
    let watchdogHandle = null

    function cleanupTimers() {
      if (timeoutHandle) {
        clearTimeout(timeoutHandle)
      }
      if (hardTimeoutHandle) {
        clearTimeout(hardTimeoutHandle)
      }
      if (watchdogHandle) {
        clearTimeout(watchdogHandle)
      }
    }

    if (typeof timeoutMs === "number" && timeoutMs > 0) {
      timeoutHandle = setTimeout(() => {
        timedOut = true
        killChildProcess(child)

        hardTimeoutHandle = setTimeout(() => {
          killChildProcess(child)
        }, 10_000)

        watchdogHandle = setTimeout(() => {
          settle({
            exitCode: -1,
            signal: "TIMEOUT",
            timedOut: true,
            stdout,
            stderr: `${stderr}\nCommand timed out and required watchdog termination.`,
            durationMs: Date.now() - start
          })
        }, 20_000)
      }, timeoutMs)
    }

    child.on("close", (exitCode, signal) => {
      cleanupTimers()

      settle({
        exitCode: typeof exitCode === "number" ? exitCode : -1,
        signal: signal ?? null,
        timedOut,
        stdout,
        stderr,
        durationMs: Date.now() - start
      })
    })

    child.on("error", (error) => {
      cleanupTimers()

      settle({
        exitCode: -1,
        signal: null,
        timedOut,
        stdout,
        stderr: `${stderr}\n${error.message}`,
        durationMs: Date.now() - start,
        error
      })
    })
  })
}

export async function runAndRequireSuccess(command, args, options = {}) {
  const result = await runCommand(command, args, options)
  if (result.exitCode !== 0) {
    const reason = [`Command failed: ${command} ${args.join(" ")}`, `exit=${result.exitCode}`]
    if (result.stderr) {
      reason.push(result.stderr)
    }
    throw new Error(reason.join("\n"))
  }
  return result
}

export async function commandExists(command, cwd) {
  const check = process.platform === "win32" ? "where" : "which"
  const result = await runCommand(check, [command], {
    cwd,
    captureOutput: true,
    timeoutMs: 20_000,
    shell: false
  })

  return result.exitCode === 0
}
