import fs from "node:fs/promises"
import path from "node:path"
import { CAPTURE_MARKERS, CAPTURE_TIMESTAMP_DEFAULTS_MS } from "./constants.mjs"

const EXTERNAL_CAPTURE_PLAN_CANDIDATES = [
  "apps/keystone/lib/pitch-engine/capture-plan.json",
  "apps/keystone/lib/pitch-engine/capture_plan.json",
  "apps/keystone/scripts/pitch-engine/capture-plan.json",
  "apps/keystone/scripts/pitch-engine/capture-plan.mjs"
]

function normalizeTimestamps(values) {
  return [...new Set(values.filter((value) => Number.isInteger(value) && value >= 0))].sort((a, b) => a - b)
}

function normalizeMarkers(markers) {
  const items = []

  for (const marker of markers ?? []) {
    if (!marker || typeof marker !== "object") {
      continue
    }
    const tMs = Number(marker.tMs)
    if (!Number.isInteger(tMs) || tMs < 0) {
      continue
    }
    const id = String(marker.id ?? `marker-${tMs}`)
    const kind = String(marker.kind ?? "custom")
    items.push({
      id,
      tMs,
      kind
    })
  }

  const withDefaults = [...items, ...CAPTURE_MARKERS]
  const unique = new Map()

  for (const marker of withDefaults) {
    unique.set(`${marker.id}:${marker.tMs}`, marker)
  }

  return [...unique.values()].sort((a, b) => a.tMs - b.tMs || a.id.localeCompare(b.id))
}

async function loadExternalCapturePlan(repoRoot) {
  for (const relativePath of EXTERNAL_CAPTURE_PLAN_CANDIDATES) {
    const absolutePath = path.resolve(repoRoot, relativePath)

    try {
      const stat = await fs.stat(absolutePath)
      if (!stat.isFile()) {
        continue
      }

      if (absolutePath.endsWith(".json")) {
        const payload = await fs.readFile(absolutePath, "utf8")
        return {
          source: relativePath,
          value: JSON.parse(payload)
        }
      }

      if (absolutePath.endsWith(".mjs")) {
        const moduleUrl = new URL(`file://${absolutePath.replace(/\\/g, "/")}`)
        const imported = await import(moduleUrl.href)
        return {
          source: relativePath,
          value: imported.default ?? imported.capturePlan ?? imported
        }
      }
    } catch {
      // ignore and continue to next candidate
    }
  }

  return null
}

export async function resolveCapturePlan(program, mode, repoRoot) {
  const external = await loadExternalCapturePlan(repoRoot)

  const planBySequence = new Map()
  if (external?.value && typeof external.value === "object") {
    const externalEntries = Array.isArray(external.value)
      ? external.value
      : Array.isArray(external.value.sequences)
        ? external.value.sequences
        : []

    for (const entry of externalEntries) {
      if (!entry || typeof entry !== "object") {
        continue
      }
      const sequenceId = String(entry.sequenceId ?? entry.slug ?? "")
      if (sequenceId.length === 0) {
        continue
      }
      planBySequence.set(sequenceId, {
        timestampsMs: normalizeTimestamps(
          Array.isArray(entry.timestampsMs) ? entry.timestampsMs.map((item) => Number(item)) : []
        ),
        markers: normalizeMarkers(entry.markers)
      })
    }
  }

  const smokeMode = mode === "smoke"

  const sequences = program.sequences.map((sequence) => {
    const fromExternal = planBySequence.get(sequence.sequenceId) ?? planBySequence.get(sequence.slug)
    const defaults = sequence.capturePlan?.timestampsMs ?? CAPTURE_TIMESTAMP_DEFAULTS_MS
    const mergedTimestamps = normalizeTimestamps([
      ...defaults,
      ...(fromExternal?.timestampsMs ?? []),
      ...CAPTURE_MARKERS.map((marker) => marker.tMs)
    ])

    const chosenTimestamps = smokeMode
      ? mergedTimestamps.filter((timestamp, index) => timestamp % 800 === 0 || index === 0)
      : mergedTimestamps

    const markers = normalizeMarkers([
      ...(sequence.capturePlan?.markers ?? []),
      ...(fromExternal?.markers ?? [])
    ])

    return {
      sequenceId: sequence.sequenceId,
      sceneId: sequence.sceneId,
      route: sequence.route,
      source: external?.source ?? "default",
      timestampsMs: chosenTimestamps,
      markers,
      markerCaptureTimestampsMs: normalizeTimestamps(markers.map((marker) => marker.tMs))
    }
  })

  return {
    source: external?.source ?? "internal-defaults",
    mode,
    generatedAtUtc: new Date().toISOString(),
    sequences
  }
}

export function summarizeCapturePlan(capturePlan) {
  return capturePlan.sequences.map((sequence) => ({
    sequenceId: sequence.sequenceId,
    timestampCount: sequence.timestampsMs.length,
    markerCount: sequence.markers.length,
    firstTimestampMs: sequence.timestampsMs[0] ?? 0,
    lastTimestampMs: sequence.timestampsMs[sequence.timestampsMs.length - 1] ?? 0
  }))
}
