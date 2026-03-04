import { SAFE_ID_PATTERN } from "./constants.mjs"
import { ValidationError } from "./errors.mjs"

function normalizeKey(rawKey) {
  return rawKey.replace(/^-+/, "")
}

function coerceValue(raw) {
  if (raw === "true") {
    return true
  }
  if (raw === "false") {
    return false
  }
  if (/^-?\d+$/.test(raw)) {
    const intValue = Number.parseInt(raw, 10)
    if (Number.isSafeInteger(intValue)) {
      return intValue
    }
  }
  if (/^-?\d+\.\d+$/.test(raw)) {
    const floatValue = Number.parseFloat(raw)
    if (Number.isFinite(floatValue)) {
      return floatValue
    }
  }
  return raw
}

export function parseCliArgs(argv = process.argv.slice(2)) {
  const positional = []
  const flags = {}

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index]

    if (token === "--") {
      positional.push(...argv.slice(index + 1))
      break
    }

    if (!token.startsWith("-")) {
      positional.push(token)
      continue
    }

    if (token.startsWith("--")) {
      const eqIndex = token.indexOf("=")
      if (eqIndex > -1) {
        const key = normalizeKey(token.slice(0, eqIndex))
        const value = coerceValue(token.slice(eqIndex + 1))
        assignFlag(flags, key, value)
        continue
      }

      const key = normalizeKey(token)
      const next = argv[index + 1]
      if (next !== undefined && !next.startsWith("-")) {
        assignFlag(flags, key, coerceValue(next))
        index += 1
        continue
      }

      assignFlag(flags, key, true)
      continue
    }

    const shortFlags = token.slice(1).split("")
    for (const short of shortFlags) {
      assignFlag(flags, short, true)
    }
  }

  return {
    flags,
    positional
  }
}

function assignFlag(target, key, value) {
  if (Object.prototype.hasOwnProperty.call(target, key)) {
    const current = target[key]
    if (Array.isArray(current)) {
      current.push(value)
      return
    }
    target[key] = [current, value]
    return
  }

  target[key] = value
}

export function flagString(flags, names, defaultValue = undefined) {
  for (const name of names) {
    if (!Object.prototype.hasOwnProperty.call(flags, name)) {
      continue
    }
    const value = flags[name]
    if (typeof value === "string") {
      return value
    }
    if (typeof value === "number") {
      return String(value)
    }
    if (Array.isArray(value)) {
      const firstString = value.find((entry) => typeof entry === "string" || typeof entry === "number")
      if (firstString !== undefined) {
        return String(firstString)
      }
    }
  }

  return defaultValue
}

export function flagNumber(flags, names, defaultValue = undefined) {
  const raw = flagString(flags, names)
  if (raw === undefined) {
    return defaultValue
  }
  const parsed = Number(raw)
  if (!Number.isFinite(parsed)) {
    throw new ValidationError(`Expected numeric flag for ${names.join("/")}.`, {
      names,
      value: raw
    })
  }
  return parsed
}

export function flagBoolean(flags, names, defaultValue = false) {
  for (const name of names) {
    if (!Object.prototype.hasOwnProperty.call(flags, name)) {
      continue
    }
    const value = flags[name]
    if (typeof value === "boolean") {
      return value
    }
    if (typeof value === "string") {
      const lowered = value.toLowerCase()
      if (lowered === "true" || lowered === "1" || lowered === "yes") {
        return true
      }
      if (lowered === "false" || lowered === "0" || lowered === "no") {
        return false
      }
    }
    if (typeof value === "number") {
      return value !== 0
    }
    if (Array.isArray(value)) {
      return flagBoolean({ [name]: value[value.length - 1] }, [name], defaultValue)
    }
    return true
  }

  return defaultValue
}

export function ensureId(name, value) {
  if (typeof value !== "string" || value.length === 0) {
    throw new ValidationError(`Missing required ${name}.`, { name, value })
  }

  if (!SAFE_ID_PATTERN.test(value)) {
    throw new ValidationError(`Invalid ${name}. Use [a-zA-Z0-9._-] and max length 128.`, {
      name,
      value
    })
  }

  return value
}

export function toBooleanEnv(value, fallback = false) {
  if (value === undefined || value === null) {
    return fallback
  }
  const normalized = String(value).trim().toLowerCase()
  if (["1", "true", "yes", "y", "on"].includes(normalized)) {
    return true
  }
  if (["0", "false", "no", "n", "off"].includes(normalized)) {
    return false
  }
  return fallback
}

export function parseCsv(raw) {
  if (typeof raw !== "string") {
    return []
  }
  return raw
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0)
}

export function printHelp(lines) {
  for (const line of lines) {
    console.log(line)
  }
}

export function requireOneOf(flags, sets) {
  for (const set of sets) {
    if (set.some((name) => Object.prototype.hasOwnProperty.call(flags, name))) {
      return
    }
  }

  throw new ValidationError("Required one of expected flags was not provided.", {
    sets
  })
}

export function mergeEnvOverrides(target, mapping) {
  const output = { ...target }
  for (const [key, envName] of Object.entries(mapping)) {
    if (process.env[envName] !== undefined) {
      output[key] = process.env[envName]
    }
  }
  return output
}

export function parseJsonArg(value, contextName) {
  if (typeof value !== "string" || value.length === 0) {
    throw new ValidationError(`Expected JSON value for ${contextName}.`, {
      contextName,
      value
    })
  }

  try {
    return JSON.parse(value)
  } catch (error) {
    throw new ValidationError(`Invalid JSON for ${contextName}.`, {
      contextName,
      value,
      cause: error instanceof Error ? error.message : String(error)
    })
  }
}
