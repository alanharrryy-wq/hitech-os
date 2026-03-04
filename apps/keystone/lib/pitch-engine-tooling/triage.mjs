import path from "node:path"
import {
  ACCEPTED_STATUS,
  PENDING_STATUS,
  REJECTED_STATUS,
  TRIAGE_GUARDRAILS,
  TRIAGE_STATUS_VALUES
} from "./constants.mjs"
import {
  appendText,
  copyFileSafe,
  pathExists,
  readJsonIfExists,
  touchFile,
  writeJsonFile,
  writeTextFile
} from "./fs-utils.mjs"
import {
  resolveBaselineSequenceDir,
  resolveProgramRunDir,
  resolveSceneDecisionFile,
  resolveSceneNotesFile,
  resolveSequenceDecisionPath,
  resolveSequenceDir,
  resolveSequenceFramesDir,
  toRelativeFromArtifacts
} from "./paths.mjs"
import { sanitizeId } from "./windows-safe.mjs"

function nowIso() {
  return new Date().toISOString()
}

function ensureStatus(status) {
  if (!TRIAGE_STATUS_VALUES.includes(status)) {
    throw new Error(`Invalid triage status: ${status}`)
  }
  return status
}

async function ensureDirectoryExists(targetPath, context) {
  if (!(await pathExists(targetPath))) {
    throw new Error(`Missing required path for triage: ${targetPath} (${context})`)
  }
}

export async function setSequenceDecision(options) {
  const {
    programId,
    runId,
    sequenceId,
    actor = "unknown",
    status,
    reason = null,
    metadata = {}
  } = options

  const normalizedStatus = ensureStatus(status)
  const sequenceDir = resolveSequenceDir(programId, runId, sequenceId)
  await ensureDirectoryExists(sequenceDir, "sequence")

  const decisionPath = resolveSequenceDecisionPath(programId, runId, sequenceId)
  const existing = await readJsonIfExists(decisionPath, {
    history: []
  })

  const record = {
    status: normalizedStatus,
    actor: String(actor).slice(0, TRIAGE_GUARDRAILS.maxActorLength),
    reason: reason ? String(reason).slice(0, TRIAGE_GUARDRAILS.maxNoteLength) : null,
    metadata,
    decidedAtUtc: nowIso()
  }

  const payload = {
    current: record,
    history: [...(existing.history ?? []), record]
  }

  await writeJsonFile(decisionPath, payload)

  return {
    programId,
    runId,
    sequenceId,
    status: normalizedStatus,
    decisionPath: toRelativeFromArtifacts(decisionPath)
  }
}

export async function appendSequenceNotes(options) {
  const { programId, runId, sequenceId, actor = "unknown", note } = options
  if (typeof note !== "string" || note.trim().length === 0) {
    throw new Error("Note text is required.")
  }

  const clippedNote = note.trim().slice(0, TRIAGE_GUARDRAILS.maxNoteLength)
  const notesPath = path.join(resolveSequenceDir(programId, runId, sequenceId), "DIFF_NOTES.md")

  if (!(await pathExists(notesPath))) {
    const bootstrap = `${TRIAGE_GUARDRAILS.noteHeading}\n\n`
    await writeTextFile(notesPath, bootstrap)
  }

  const block = [
    `${TRIAGE_GUARDRAILS.noteSectionPrefix} ${nowIso()}`,
    `${TRIAGE_GUARDRAILS.noteActorPrefix} ${String(actor).slice(0, TRIAGE_GUARDRAILS.maxActorLength)}`,
    `${TRIAGE_GUARDRAILS.noteTextPrefix} ${clippedNote}`,
    ""
  ].join("\n")

  await appendText(notesPath, block)

  return {
    programId,
    runId,
    sequenceId,
    notesPath: toRelativeFromArtifacts(notesPath),
    appended: true
  }
}

export async function acceptSequenceBaseline(options) {
  const { programId, runId, sequenceId, actor = "unknown", reason = null } = options

  const framesDir = resolveSequenceFramesDir(programId, runId, sequenceId)
  await ensureDirectoryExists(framesDir, "sequence frames")

  const baselineDir = resolveBaselineSequenceDir(programId, sequenceId)
  const files = await import("node:fs/promises").then(async (fsp) => {
    const entries = await fsp.readdir(framesDir, { withFileTypes: true })
    return entries.filter((entry) => entry.isFile() && entry.name.endsWith(".png")).map((entry) => entry.name)
  })

  files.sort((a, b) => a.localeCompare(b))

  if (files.length === 0) {
    throw new Error("No frame PNG files found for sequence baseline acceptance.")
  }

  for (const fileName of files) {
    await copyFileSafe(path.join(framesDir, fileName), path.join(baselineDir, fileName))
  }

  await setSequenceDecision({
    programId,
    runId,
    sequenceId,
    actor,
    status: ACCEPTED_STATUS,
    reason,
    metadata: {
      acceptedFrameCount: files.length,
      baselineDir: toRelativeFromArtifacts(baselineDir)
    }
  })

  return {
    programId,
    runId,
    sequenceId,
    baselineDir: toRelativeFromArtifacts(baselineDir),
    acceptedFrameCount: files.length,
    actor
  }
}

export async function rejectSequence(options) {
  const { programId, runId, sequenceId, actor = "unknown", reason = null } = options

  await setSequenceDecision({
    programId,
    runId,
    sequenceId,
    actor,
    status: REJECTED_STATUS,
    reason,
    metadata: {
      rejectedAtUtc: nowIso()
    }
  })

  return {
    programId,
    runId,
    sequenceId,
    status: REJECTED_STATUS,
    actor
  }
}

export async function markSequencePending(options) {
  const { programId, runId, sequenceId, actor = "unknown" } = options

  await setSequenceDecision({
    programId,
    runId,
    sequenceId,
    actor,
    status: PENDING_STATUS,
    metadata: {
      pendingAtUtc: nowIso()
    }
  })

  return {
    programId,
    runId,
    sequenceId,
    status: PENDING_STATUS
  }
}

export async function setSceneDecision(options) {
  const { sceneId, runId, status, actor = "unknown", reason = null, metadata = {} } = options
  const normalizedStatus = ensureStatus(status)

  const decisionPath = resolveSceneDecisionFile(sceneId, runId)
  const payload = await readJsonIfExists(decisionPath, {
    sceneId,
    runId,
    history: []
  })

  const entry = {
    status: normalizedStatus,
    actor: String(actor).slice(0, TRIAGE_GUARDRAILS.maxActorLength),
    reason: reason ? String(reason).slice(0, TRIAGE_GUARDRAILS.maxNoteLength) : null,
    metadata,
    decidedAtUtc: nowIso()
  }

  payload.current = entry
  payload.history = [...(payload.history ?? []), entry]

  await writeJsonFile(decisionPath, payload)

  return {
    sceneId,
    runId,
    status: normalizedStatus,
    decisionPath: toRelativeFromArtifacts(decisionPath)
  }
}

export async function appendSceneNotes(options) {
  const { sceneId, runId, actor = "unknown", note } = options
  if (typeof note !== "string" || note.trim().length === 0) {
    throw new Error("Note text is required.")
  }

  const notesPath = resolveSceneNotesFile(sceneId, runId)

  if (!(await pathExists(notesPath))) {
    await writeTextFile(notesPath, `${TRIAGE_GUARDRAILS.noteHeading}\n\n`)
  }

  const payload = [
    `${TRIAGE_GUARDRAILS.noteSectionPrefix} ${nowIso()}`,
    `${TRIAGE_GUARDRAILS.noteActorPrefix} ${String(actor).slice(0, TRIAGE_GUARDRAILS.maxActorLength)}`,
    `${TRIAGE_GUARDRAILS.noteTextPrefix} ${note.trim().slice(0, TRIAGE_GUARDRAILS.maxNoteLength)}`,
    ""
  ].join("\n")

  await appendText(notesPath, payload)

  return {
    sceneId,
    runId,
    notesPath: toRelativeFromArtifacts(notesPath),
    appended: true
  }
}

export async function guardRunAndSequence(programId, runId, sequenceId) {
  const runPath = resolveProgramRunDir(programId, runId)
  const sequencePath = resolveSequenceDir(programId, runId, sequenceId)

  await ensureDirectoryExists(runPath, "run")
  await ensureDirectoryExists(sequencePath, "sequence")

  return {
    runPath,
    sequencePath
  }
}

export function buildTriageReferenceId(sceneOrSequenceId, runId) {
  return `${sanitizeId(sceneOrSequenceId)}--${sanitizeId(runId)}`
}

export async function ensureDiffNotesFile(targetPath) {
  if (!(await pathExists(targetPath))) {
    await touchFile(targetPath, `${TRIAGE_GUARDRAILS.noteHeading}\n\n`)
  }
  return targetPath
}
