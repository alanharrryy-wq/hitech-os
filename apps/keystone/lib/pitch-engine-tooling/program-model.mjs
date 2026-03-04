import {
  PITCH_DECK_FIXTURE,
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES,
  getPitchDeck,
  getPitchScreenBySlug
} from "@hitech/contracts"
import { CAPTURE_MARKERS, CAPTURE_TIMESTAMP_DEFAULTS_MS, SCENE_SCHEMA_VERSION } from "./constants.mjs"
import { sanitizeId } from "./windows-safe.mjs"

function buildDefaultCapturePlan(sequenceId) {
  return {
    sequenceId,
    timestampsMs: [...CAPTURE_TIMESTAMP_DEFAULTS_MS],
    markers: CAPTURE_MARKERS.map((marker) => ({
      ...marker,
      sequenceId
    }))
  }
}

function buildSequence(screen) {
  const sequenceId = sanitizeId(screen.slug)
  const sceneId = sanitizeId(`${screen.slug}--scene`)

  return {
    sequenceId,
    sceneId,
    slug: screen.slug,
    route: screen.route,
    title: screen.title,
    order: screen.order,
    schemaVersion: SCENE_SCHEMA_VERSION,
    meta: {
      tag: screen.tag,
      canonicalRoute: PITCH_ROUTES[screen.slug],
      canonicalTitle: PITCH_SCREEN_TITLES[screen.slug]
    },
    capturePlan: buildDefaultCapturePlan(sequenceId)
  }
}

export function resolveProgram(programId = "default-program") {
  const deck = getPitchDeck()

  const sequences = PITCH_SCREEN_ORDER.map((slug) => {
    const screen = getPitchScreenBySlug(slug)
    return buildSequence(screen)
  })

  return {
    programId: sanitizeId(programId),
    deckId: deck.meta.deckId,
    deckVersion: deck.meta.version,
    locale: deck.meta.locale,
    generatedAtUtc: new Date().toISOString(),
    sequenceCount: sequences.length,
    sequences,
    captureDefaults: {
      timestampsMs: [...CAPTURE_TIMESTAMP_DEFAULTS_MS],
      markerCount: CAPTURE_MARKERS.length
    }
  }
}

export function resolveSequence(program, sequenceId) {
  const normalized = sanitizeId(sequenceId)
  const match = program.sequences.find((entry) => entry.sequenceId === normalized || entry.slug === sequenceId)
  if (!match) {
    throw new Error(`Sequence not found in program: ${sequenceId}`)
  }
  return match
}

export function listProgramSceneIds(program) {
  return program.sequences.map((sequence) => sequence.sceneId)
}

export function extractCaptureTimeline(program) {
  return program.sequences.map((sequence) => ({
    sequenceId: sequence.sequenceId,
    sceneId: sequence.sceneId,
    route: sequence.route,
    timestampsMs: [...sequence.capturePlan.timestampsMs],
    markers: sequence.capturePlan.markers.map((marker) => ({ ...marker }))
  }))
}

export function selectProgramMode(mode) {
  if (mode === "smoke") {
    return {
      mode,
      includeIntermediates: false,
      includeAllSequences: true,
      runIntent: "smoke-validation"
    }
  }

  if (mode === "full") {
    return {
      mode,
      includeIntermediates: true,
      includeAllSequences: true,
      runIntent: "full-render"
    }
  }

  return {
    mode,
    includeIntermediates: true,
    includeAllSequences: true,
    runIntent: "baseline-update"
  }
}

export function ensureCanonicalProgram(program) {
  if (!program || typeof program !== "object") {
    throw new Error("Invalid program payload.")
  }

  if (!Array.isArray(program.sequences) || program.sequences.length === 0) {
    throw new Error("Program has no sequences.")
  }

  for (const [index, sequence] of program.sequences.entries()) {
    const expectedSlug = PITCH_SCREEN_ORDER[index]
    if (sequence.slug !== expectedSlug) {
      throw new Error(`Program sequence order mismatch at index ${index}.`) // deterministic invariant
    }

    if (sequence.route !== PITCH_ROUTES[sequence.slug]) {
      throw new Error(`Program route mismatch for ${sequence.slug}.`)
    }
  }

  return program
}

export function resolveCapturePlanFromProgram(program, mode) {
  const selection = selectProgramMode(mode)

  return program.sequences.map((sequence) => {
    const timestamps = selection.includeIntermediates
      ? sequence.capturePlan.timestampsMs
      : sequence.capturePlan.timestampsMs.filter((value) => value % 800 === 0)

    const markerTimestamps = sequence.capturePlan.markers.map((marker) => marker.tMs)
    const merged = new Set([...timestamps, ...markerTimestamps])

    return {
      sequenceId: sequence.sequenceId,
      sceneId: sequence.sceneId,
      route: sequence.route,
      timestampsMs: [...merged].sort((a, b) => a - b),
      markers: sequence.capturePlan.markers.map((marker) => ({ ...marker }))
    }
  })
}

export function buildSceneSchemaEnvelope(programId, runId, sequence) {
  return {
    schemaVersion: SCENE_SCHEMA_VERSION,
    canonicalUrl: `/pitch/${sequence.slug}`,
    programId,
    runId,
    sequenceId: sequence.sequenceId,
    sceneId: sequence.sceneId,
    route: sequence.route,
    slug: sequence.slug,
    title: sequence.title,
    metadata: {
      tag: sequence.meta.tag,
      canonicalRoute: sequence.meta.canonicalRoute,
      canonicalTitle: sequence.meta.canonicalTitle
    }
  }
}

export function resolvePitchDeckSnapshot() {
  return {
    meta: {
      ...PITCH_DECK_FIXTURE.meta
    },
    navigation: {
      ...PITCH_DECK_FIXTURE.navigation,
      links: PITCH_DECK_FIXTURE.navigation.links.map((link) => ({ ...link }))
    }
  }
}
