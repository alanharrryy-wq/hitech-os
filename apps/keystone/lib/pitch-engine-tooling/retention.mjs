import path from "node:path"
import {
  PITCH_RUNS_PER_PROGRAM_DEFAULT,
  RETENTION_POLICY_DEFAULT,
  SCENE_RUNS_PER_OWNER_DEFAULT
} from "./constants.mjs"
import {
  listDirectories,
  pathExists,
  readDirectoryDetailed,
  readJsonIfExists,
  removeDirectory,
  touchFile,
  writeJsonFile
} from "./fs-utils.mjs"
import {
  resolvePitchRetentionMetadataPath,
  resolveProgramDir,
  resolveProgramRunDir,
  resolveRunPinMarkerPath,
  resolveSceneRetentionDir,
  resolveSharedRetentionPath,
  toRelativeFromArtifacts
} from "./paths.mjs"

function parseRunSortKey(runId) {
  const compact = runId.replace(/[^0-9]/g, "")
  if (compact.length >= 8) {
    const parsed = Number.parseInt(compact.slice(0, 14), 10)
    if (Number.isFinite(parsed)) {
      return parsed
    }
  }
  return Number.MIN_SAFE_INTEGER
}

async function isPinned(programId, runId) {
  const markerPath = resolveRunPinMarkerPath(programId, runId)
  return pathExists(markerPath)
}

function sortRuns(runIds) {
  return [...runIds].sort((left, right) => {
    const leftScore = parseRunSortKey(left)
    const rightScore = parseRunSortKey(right)

    if (leftScore !== rightScore) {
      return rightScore - leftScore
    }

    return right.localeCompare(left)
  })
}

export async function pinRun(programId, runId, actor = "system") {
  const markerPath = resolveRunPinMarkerPath(programId, runId)
  await touchFile(markerPath, `Pinned by ${actor} at ${new Date().toISOString()}\n`)
  return {
    programId,
    runId,
    markerPath: toRelativeFromArtifacts(markerPath),
    pinned: true
  }
}

export async function unpinRun(programId, runId) {
  const markerPath = resolveRunPinMarkerPath(programId, runId)
  const exists = await pathExists(markerPath)
  if (!exists) {
    return {
      programId,
      runId,
      markerPath: toRelativeFromArtifacts(markerPath),
      removed: false
    }
  }

  await removeDirectory(markerPath)
  return {
    programId,
    runId,
    markerPath: toRelativeFromArtifacts(markerPath),
    removed: true
  }
}

export async function pruneProgramRuns(programId, options = {}) {
  const keepLast = Number.isInteger(options.keepLast)
    ? Math.max(1, options.keepLast)
    : PITCH_RUNS_PER_PROGRAM_DEFAULT

  const policy = {
    ...RETENTION_POLICY_DEFAULT,
    keepLast
  }

  const programDir = resolveProgramDir(programId)
  const runIds = await listDirectories(programDir)
  const candidateRuns = runIds.filter((runId) => /^\d{8}_\d{6}_[a-zA-Z0-9]+$/.test(runId))
  const sorted = sortRuns(candidateRuns)

  const kept = []
  const deleted = []
  const pinned = []

  for (let index = 0; index < sorted.length; index += 1) {
    const runId = sorted[index]
    const pinnedRun = await isPinned(programId, runId)

    if (index < keepLast || pinnedRun) {
      if (pinnedRun) {
        pinned.push(runId)
      }
      kept.push(runId)
      continue
    }

    const runPath = resolveProgramRunDir(programId, runId)
    await removeDirectory(runPath)
    deleted.push(runId)
  }

  const metadata = {
    programId,
    keepLast,
    policy,
    generatedAtUtc: new Date().toISOString(),
    counts: {
      total: sorted.length,
      kept: kept.length,
      deleted: deleted.length,
      pinned: pinned.length
    },
    kept,
    pinned,
    deleted
  }

  await writeJsonFile(resolvePitchRetentionMetadataPath(programId), metadata)
  await writeSharedRetentionSummary(programId, metadata)

  return metadata
}

async function writeSharedRetentionSummary(programId, programMetadata) {
  const root = resolveSharedRetentionPath()
  const summaryPath = path.join(root, "summary.json")
  const existing = await readJsonIfExists(summaryPath, {
    version: 1,
    updatedAtUtc: null,
    programs: {}
  })

  existing.programs[programId] = {
    keepLast: programMetadata.keepLast,
    counts: programMetadata.counts,
    updatedAtUtc: new Date().toISOString()
  }

  const sortedProgramIds = Object.keys(existing.programs).sort((a, b) => a.localeCompare(b))
  const normalizedPrograms = {}
  for (const key of sortedProgramIds) {
    normalizedPrograms[key] = existing.programs[key]
  }

  const payload = {
    version: 1,
    updatedAtUtc: new Date().toISOString(),
    programs: normalizedPrograms
  }

  await writeJsonFile(summaryPath, payload)
}

export async function enforceSceneRetention(owner = "scene-studio", keepLast = SCENE_RUNS_PER_OWNER_DEFAULT) {
  const retentionDir = resolveSceneRetentionDir()
  const details = await readDirectoryDetailed(retentionDir)
  const files = details.filter((entry) => entry.isFile).sort((a, b) => b.mtimeMs - a.mtimeMs)

  const kept = []
  const deleted = []

  for (let index = 0; index < files.length; index += 1) {
    const entry = files[index]
    const absolute = entry.absolute

    if (index < keepLast) {
      kept.push(path.basename(absolute))
      continue
    }

    await import("node:fs/promises").then((fsp) => fsp.rm(absolute, { force: true }))
    deleted.push(path.basename(absolute))
  }

  const metadata = {
    owner,
    keepLast,
    generatedAtUtc: new Date().toISOString(),
    kept,
    deleted
  }

  await writeJsonFile(path.join(retentionDir, `${owner}-retention.json`), metadata)
  return metadata
}
