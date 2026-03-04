import crypto from "node:crypto"

export function stableSortObject(value) {
  if (Array.isArray(value)) {
    return value.map((entry) => stableSortObject(entry))
  }

  if (value !== null && typeof value === "object") {
    const output = {}
    const keys = Object.keys(value).sort((a, b) => a.localeCompare(b))
    for (const key of keys) {
      output[key] = stableSortObject(value[key])
    }
    return output
  }

  return value
}

export function stableJsonStringify(value, indent = 2) {
  return JSON.stringify(stableSortObject(value), null, indent) + "\n"
}

export function stableHash(value) {
  const canonical = typeof value === "string" ? value : stableJsonStringify(value, 0)
  return crypto.createHash("sha256").update(canonical).digest("hex")
}

export function deterministicNow(referenceIso = "1970-01-01T00:00:00.000Z") {
  return new Date(referenceIso).toISOString()
}

export function stableUnique(items) {
  return [...new Set(items)].sort((a, b) => String(a).localeCompare(String(b)))
}

export function stableCompareBy(fields) {
  return (left, right) => {
    for (const field of fields) {
      const a = left?.[field]
      const b = right?.[field]

      if (a === b) {
        continue
      }

      if (a === undefined || a === null) {
        return -1
      }
      if (b === undefined || b === null) {
        return 1
      }

      if (typeof a === "number" && typeof b === "number") {
        return a - b
      }

      const stringCompare = String(a).localeCompare(String(b))
      if (stringCompare !== 0) {
        return stringCompare
      }
    }

    return 0
  }
}

export function toSortedEntries(record) {
  return Object.entries(record).sort((a, b) => a[0].localeCompare(b[0]))
}

export function deterministicChunks(items, size) {
  if (!Number.isInteger(size) || size <= 0) {
    throw new Error("Chunk size must be a positive integer.")
  }

  const sorted = [...items]
  sorted.sort((a, b) => String(a).localeCompare(String(b)))

  const chunks = []
  for (let index = 0; index < sorted.length; index += size) {
    chunks.push(sorted.slice(index, index + size))
  }
  return chunks
}

export function deterministicShuffle(items, seed = "pitch-engine") {
  const output = [...items]

  for (let index = output.length - 1; index > 0; index -= 1) {
    const hash = crypto
      .createHash("sha256")
      .update(`${seed}:${index}:${JSON.stringify(output[index])}`)
      .digest("hex")
    const parsed = Number.parseInt(hash.slice(0, 8), 16)
    const swapIndex = parsed % (index + 1)
    const temp = output[index]
    output[index] = output[swapIndex]
    output[swapIndex] = temp
  }

  return output
}

export function stableMergeArrayByKey(items, key) {
  const map = new Map()

  for (const item of items) {
    if (!item || typeof item !== "object") {
      continue
    }
    const itemKey = item[key]
    if (itemKey === undefined || itemKey === null) {
      continue
    }
    map.set(String(itemKey), item)
  }

  return [...map.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map((entry) => entry[1])
}

export function normalizeWhitespace(input) {
  return String(input)
    .replace(/\r\n/g, "\n")
    .replace(/[ \t]+\n/g, "\n")
    .trim()
}

export function stableTimestampId(date = new Date()) {
  const iso = date.toISOString()
  const compact = iso.replace(/[-:]/g, "").replace(/\..+$/, "")
  return compact.replace("T", "_")
}
