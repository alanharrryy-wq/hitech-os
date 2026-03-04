import path from "node:path"
import { SAFE_ID_PATTERN, WINDOW_SAFE_FILENAME_PATTERN } from "./constants.mjs"
import { ValidationError } from "./errors.mjs"

const RESERVED_WINDOWS_NAMES = new Set([
  "CON",
  "PRN",
  "AUX",
  "NUL",
  "COM1",
  "COM2",
  "COM3",
  "COM4",
  "COM5",
  "COM6",
  "COM7",
  "COM8",
  "COM9",
  "LPT1",
  "LPT2",
  "LPT3",
  "LPT4",
  "LPT5",
  "LPT6",
  "LPT7",
  "LPT8",
  "LPT9"
])

export function sanitizeId(input, fallback = "value") {
  const normalized = String(input ?? "")
    .trim()
    .replace(/[\\/:*?"<>|]+/g, "-")
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9._-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^[-._]+/, "")
    .replace(/[-._]+$/, "")

  const candidate = normalized.length > 0 ? normalized : fallback
  const clipped = candidate.slice(0, 128)

  if (RESERVED_WINDOWS_NAMES.has(clipped.toUpperCase())) {
    return `${clipped}-id`
  }

  if (!SAFE_ID_PATTERN.test(clipped)) {
    return `${fallback}-id`
  }

  return clipped
}

export function validateSafeId(name, value) {
  if (typeof value !== "string") {
    throw new ValidationError(`${name} must be a string.`, { name, value })
  }

  if (!SAFE_ID_PATTERN.test(value)) {
    throw new ValidationError(`${name} is not path-safe.`, { name, value })
  }

  if (RESERVED_WINDOWS_NAMES.has(value.toUpperCase())) {
    throw new ValidationError(`${name} cannot use a reserved Windows name.`, {
      name,
      value
    })
  }

  return value
}

export function safeJoin(basePath, ...segments) {
  const normalizedSegments = segments.map((segment, index) => {
    const value = sanitizeId(segment, `segment-${index + 1}`)
    validateSafeFilename(value)
    return value
  })

  const resolved = path.resolve(basePath, ...normalizedSegments)
  assertPathInside(basePath, resolved)
  return resolved
}

export function assertPathInside(basePath, candidatePath) {
  const base = path.resolve(basePath)
  const candidate = path.resolve(candidatePath)
  const baseNormalized = base.toLowerCase()
  const candidateNormalized = candidate.toLowerCase()

  if (candidateNormalized === baseNormalized) {
    return
  }

  const prefix = baseNormalized.endsWith(path.sep.toLowerCase())
    ? baseNormalized
    : `${baseNormalized}${path.sep.toLowerCase()}`

  if (!candidateNormalized.startsWith(prefix)) {
    throw new ValidationError("Resolved path escaped the allowed base path.", {
      base,
      candidate
    })
  }
}

export function normalizePathForReport(inputPath) {
  return String(inputPath).replace(/\\/g, "/")
}

export function splitSafePath(inputPath) {
  return normalizePathForReport(inputPath)
    .split("/")
    .map((segment) => segment.trim())
    .filter((segment) => segment.length > 0)
}

export function validateSafeFilename(value) {
  if (typeof value !== "string" || !WINDOW_SAFE_FILENAME_PATTERN.test(value)) {
    throw new ValidationError("Unsafe filename.", { value })
  }

  if (RESERVED_WINDOWS_NAMES.has(value.toUpperCase())) {
    throw new ValidationError("Reserved Windows filename.", { value })
  }

  return value
}

export function toWindowsSafeRelative(input) {
  return splitSafePath(input)
    .map((segment, index) => sanitizeId(segment, `segment-${index + 1}`))
    .join("/")
}

export function ensureNoTraversal(value) {
  if (value.includes("..")) {
    throw new ValidationError("Path traversal token '..' is not allowed.", {
      value
    })
  }

  if (value.includes("\\") || value.includes("/")) {
    throw new ValidationError("Expected single ID value, got path separators.", {
      value
    })
  }

  return value
}

export function makeSafeSceneId(programId, sequenceId, suffix = "scene") {
  const parts = [programId, sequenceId, suffix].map((entry) => sanitizeId(entry, "item"))
  return parts.join("--")
}

export function buildTimestampFileName(tMs) {
  if (!Number.isInteger(tMs) || tMs < 0) {
    throw new ValidationError("Timestamp must be a positive integer.", {
      tMs
    })
  }
  return `${String(tMs).padStart(5, "0")}.png`
}

export function toPosixPath(inputPath) {
  return path.posix.normalize(normalizePathForReport(inputPath))
}
