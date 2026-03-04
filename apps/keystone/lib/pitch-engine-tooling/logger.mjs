import fs from "node:fs"
import path from "node:path"
import { TERMINAL_SYMBOLS } from "./constants.mjs"

function ts() {
  return new Date().toISOString()
}

export function createLogger(options = {}) {
  const logFile = options.logFile
  const prefix = options.prefix ?? "pitch-tooling"
  const muted = options.muted ?? false

  function write(level, message, metadata) {
    const symbol = TERMINAL_SYMBOLS[level] ?? TERMINAL_SYMBOLS.info
    const line = `${ts()} ${symbol} [${prefix}] ${message}`

    if (!muted) {
      if (level === "fail") {
        console.error(line)
      } else if (level === "warn") {
        console.warn(line)
      } else {
        console.log(line)
      }

      if (metadata !== undefined) {
        const pretty = JSON.stringify(metadata, null, 2)
        if (level === "fail") {
          console.error(pretty)
        } else {
          console.log(pretty)
        }
      }
    }

    if (typeof logFile === "string" && logFile.length > 0) {
      const parent = path.dirname(logFile)
      fs.mkdirSync(parent, { recursive: true })
      const payload = [line]
      if (metadata !== undefined) {
        payload.push(JSON.stringify(metadata))
      }
      fs.appendFileSync(logFile, payload.join("\n") + "\n", "utf8")
    }
  }

  return {
    info(message, metadata) {
      write("info", message, metadata)
    },
    pass(message, metadata) {
      write("pass", message, metadata)
    },
    warn(message, metadata) {
      write("warn", message, metadata)
    },
    fail(message, metadata) {
      write("fail", message, metadata)
    }
  }
}

export function captureCommandLog(logger, command, args, result) {
  logger.info("Command invocation", {
    command,
    args,
    exitCode: result?.exitCode,
    durationMs: result?.durationMs,
    stdout: result?.stdout,
    stderr: result?.stderr
  })
}
