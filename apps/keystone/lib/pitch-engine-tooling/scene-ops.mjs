import path from "node:path"
import { SCENE_RUNS_PER_OWNER_DEFAULT } from "./constants.mjs"
import { ensureDir, listFilesRecursive, pathExists, readJsonIfExists, touchFile, writeJsonFile, writeTextFile } from "./fs-utils.mjs"
import { writeSceneIndexFiles } from "./indexer.mjs"
import {
  resolveSceneDecisionFile,
  resolveSceneRerunDir,
  resolveSceneRerunFile,
  resolveSceneRetentionDir,
  resolveSceneTriageDir,
  toRelativeFromArtifacts
} from "./paths.mjs"
import { enforceSceneRetention } from "./retention.mjs"
import { appendSceneNotes, setSceneDecision } from "./triage.mjs"
import { sanitizeId } from "./windows-safe.mjs"

export async function ensureSceneOperationsLayout() {
  await ensureDir(resolveSceneTriageDir())
  await ensureDir(resolveSceneRetentionDir())
  await ensureDir(resolveSceneRerunDir())

  const triageIndex = path.join(resolveSceneTriageDir(), "TRIAGE_OVERVIEW.md")
  const retentionGuide = path.join(resolveSceneRetentionDir(), "RETENTION_POLICY.md")

  if (!(await pathExists(triageIndex))) {
    await writeTextFile(
      triageIndex,
      [
        "# Scene Studio Triage Overview",
        "",
        "Use CLI commands to accept/reject/rerun scenes and append notes.",
        "Generated automatically by tooling.",
        ""
      ].join("\n")
    )
  }

  if (!(await pathExists(retentionGuide))) {
    await writeTextFile(
      retentionGuide,
      [
        "# Scene Studio Retention Policy",
        "",
        `Default keep-last value: ${SCENE_RUNS_PER_OWNER_DEFAULT}`,
        "Pinned runs are retained until unpinned.",
        ""
      ].join("\n")
    )
  }

  return writeSceneIndexFiles()
}

export async function sceneTriageOverview() {
  await ensureSceneOperationsLayout()
  const files = await listFilesRecursive(resolveSceneTriageDir())

  return {
    generatedAtUtc: new Date().toISOString(),
    triageDir: toRelativeFromArtifacts(resolveSceneTriageDir()),
    files: files.map((entry) => toRelativeFromArtifacts(entry))
  }
}

export async function acceptScene(options) {
  const { sceneId, runId, actor = "scene-studio", reason = null } = options
  const result = await setSceneDecision({
    sceneId,
    runId,
    actor,
    status: "accepted",
    reason,
    metadata: {
      source: "scene-cli"
    }
  })

  await writeSceneIndexFiles()
  return result
}

export async function rejectScene(options) {
  const { sceneId, runId, actor = "scene-studio", reason = null } = options
  const result = await setSceneDecision({
    sceneId,
    runId,
    actor,
    status: "rejected",
    reason,
    metadata: {
      source: "scene-cli"
    }
  })

  await writeSceneIndexFiles()
  return result
}

export async function appendSceneNote(options) {
  const { sceneId, runId, actor = "scene-studio", note } = options
  const result = await appendSceneNotes({
    sceneId,
    runId,
    actor,
    note
  })

  await writeSceneIndexFiles()
  return result
}

export async function requestSceneRerun(options) {
  const { sceneId, actor = "scene-studio", reason = null } = options
  const requestPath = resolveSceneRerunFile(sceneId)
  const payload = {
    sceneId: sanitizeId(sceneId),
    actor,
    reason,
    requestedAtUtc: new Date().toISOString(),
    status: "queued"
  }

  await writeJsonFile(requestPath, payload)
  await writeSceneIndexFiles()

  return {
    rerunRequestPath: toRelativeFromArtifacts(requestPath),
    request: payload
  }
}

export async function pinSceneRun(options) {
  const { sceneId, runId, actor = "scene-studio" } = options
  const markerPath = path.join(resolveSceneRetentionDir(), `${sanitizeId(sceneId)}--${sanitizeId(runId)}.PIN.marker`)
  await touchFile(markerPath, `Pinned by ${actor} at ${new Date().toISOString()}\n`)

  await writeSceneIndexFiles()

  return {
    pinned: true,
    markerPath: toRelativeFromArtifacts(markerPath)
  }
}

export async function pruneSceneRuns(options = {}) {
  const keepLast = Number.isInteger(options.keepLast)
    ? Math.max(1, options.keepLast)
    : SCENE_RUNS_PER_OWNER_DEFAULT

  const retention = await enforceSceneRetention("scene-studio", keepLast)
  await writeSceneIndexFiles()
  return retention
}

export async function readSceneDecision(options) {
  const { sceneId, runId } = options
  const decisionPath = resolveSceneDecisionFile(sceneId, runId)
  const data = await readJsonIfExists(decisionPath, null)

  return {
    decisionPath: toRelativeFromArtifacts(decisionPath),
    data
  }
}
