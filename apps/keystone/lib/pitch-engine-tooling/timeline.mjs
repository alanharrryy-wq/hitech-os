import { CANONICAL_TIMELINE_VERSION, TIMELINE_PLACEHOLDER_EVENTS } from "./constants.mjs"
import { stableHash } from "./deterministic.mjs"

export function buildProgramTimeline(program, capturePlan, profile) {
  const sequences = []

  for (const sequence of capturePlan.sequences) {
    const markers = sequence.markers.map((marker) => ({
      ...marker,
      canonicalId: `${sequence.sequenceId}:${marker.id}`
    }))

    const events = TIMELINE_PLACEHOLDER_EVENTS.map((event) => ({
      ...event,
      sequenceId: sequence.sequenceId,
      sceneId: sequence.sceneId
    }))

    const stamps = sequence.timestampsMs.map((tMs) => ({
      tMs,
      marker: markers.find((marker) => marker.tMs === tMs)?.id ?? null
    }))

    sequences.push({
      sequenceId: sequence.sequenceId,
      sceneId: sequence.sceneId,
      route: sequence.route,
      profile: profile.name,
      timestampsMs: [...sequence.timestampsMs],
      markerCaptureTimestampsMs: [...sequence.markerCaptureTimestampsMs],
      markers,
      events,
      captures: stamps
    })
  }

  const totalCaptures = sequences.reduce((sum, sequence) => sum + sequence.timestampsMs.length, 0)

  return {
    timelineVersion: CANONICAL_TIMELINE_VERSION,
    generatedAtUtc: new Date().toISOString(),
    programId: program.programId,
    runProfile: profile.name,
    sequenceCount: sequences.length,
    totalCaptures,
    sequences,
    hash: stableHash({
      programId: program.programId,
      profile: profile.name,
      sequences: sequences.map((sequence) => ({
        sequenceId: sequence.sequenceId,
        timestampsMs: sequence.timestampsMs,
        markerCaptureTimestampsMs: sequence.markerCaptureTimestampsMs
      }))
    })
  }
}

export function flattenTimelineCaptures(timeline) {
  const captures = []

  for (const sequence of timeline.sequences) {
    for (const timestamp of sequence.timestampsMs) {
      captures.push({
        sequenceId: sequence.sequenceId,
        sceneId: sequence.sceneId,
        route: sequence.route,
        tMs: timestamp,
        marker: sequence.markers.find((marker) => marker.tMs === timestamp)?.id ?? null
      })
    }
  }

  return captures.sort((left, right) => {
    if (left.sequenceId !== right.sequenceId) {
      return left.sequenceId.localeCompare(right.sequenceId)
    }
    return left.tMs - right.tMs
  })
}

export function summarizeTimeline(timeline) {
  return {
    sequenceCount: timeline.sequences.length,
    totalCaptures: timeline.totalCaptures,
    firstSequenceId: timeline.sequences[0]?.sequenceId ?? null,
    lastSequenceId: timeline.sequences[timeline.sequences.length - 1]?.sequenceId ?? null,
    profile: timeline.runProfile,
    hash: timeline.hash
  }
}
