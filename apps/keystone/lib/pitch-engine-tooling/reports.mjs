import path from "node:path"
import { REPORT_SECTIONS } from "./constants.mjs"
import { writeJsonFile, writeTextFile } from "./fs-utils.mjs"
import {
  resolveProgramRunDir,
  resolveSceneDir,
  resolveSequenceDir,
  toRelativeFromArtifacts
} from "./paths.mjs"

function renderSectionHeading(title) {
  return `## ${title}`
}

function formatList(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return "- none"
  }

  return items.map((item) => `- ${item}`).join("\n")
}

export async function writeSequenceReport(options) {
  const {
    programId,
    runId,
    sequenceId,
    payload
  } = options

  const sequenceDir = resolveSequenceDir(programId, runId, sequenceId)
  const jsonPath = path.join(sequenceDir, "report.json")
  const mdPath = path.join(sequenceDir, "report.md")

  const reportPayload = {
    ...payload,
    generatedAtUtc: new Date().toISOString(),
    programId,
    runId,
    sequenceId,
    reportSections: REPORT_SECTIONS
  }

  await writeJsonFile(jsonPath, reportPayload)

  const lines = [
    `# Sequence Report ${sequenceId}`,
    "",
    `Program: \`${programId}\``,
    `Run: \`${runId}\``,
    `Generated: ${reportPayload.generatedAtUtc}`,
    "",
    renderSectionHeading("Summary"),
    `- Route: ${payload.route}`,
    `- Captures: ${payload.captureCount}`,
    `- Profile: ${payload.profile.actual}`,
    `- Degraded: ${payload.profile.degraded}`,
    "",
    renderSectionHeading("Capture Files"),
    formatList(payload.frames.map((entry) => `${entry.file} (${entry.tMs}ms)`)),
    "",
    renderSectionHeading("Warnings"),
    formatList(payload.warnings ?? []),
    ""
  ]

  await writeTextFile(mdPath, lines.join("\n") + "\n")

  return {
    jsonPath: toRelativeFromArtifacts(jsonPath),
    mdPath: toRelativeFromArtifacts(mdPath)
  }
}

export async function writeSceneReport(options) {
  const {
    programId,
    runId,
    sceneId,
    payload
  } = options

  const sceneDir = resolveSceneDir(programId, runId, sceneId)
  const jsonPath = path.join(sceneDir, "report.json")
  const mdPath = path.join(sceneDir, "report.md")

  const reportPayload = {
    ...payload,
    generatedAtUtc: new Date().toISOString(),
    programId,
    runId,
    sceneId
  }

  await writeJsonFile(jsonPath, reportPayload)

  const lines = [
    `# Scene Report ${sceneId}`,
    "",
    `Program: \`${programId}\``,
    `Run: \`${runId}\``,
    `Generated: ${reportPayload.generatedAtUtc}`,
    "",
    renderSectionHeading("Diff Assets"),
    `- before: ${payload.beforeImage}`,
    `- after: ${payload.afterImage}`,
    `- diff: ${payload.diffImage}`,
    "",
    renderSectionHeading("Decision"),
    `- status: ${payload.status}`,
    `- baselineExists: ${payload.baselineExists}`,
    "",
    renderSectionHeading("Warnings"),
    formatList(payload.warnings ?? []),
    ""
  ]

  await writeTextFile(mdPath, lines.join("\n") + "\n")

  return {
    jsonPath: toRelativeFromArtifacts(jsonPath),
    mdPath: toRelativeFromArtifacts(mdPath)
  }
}

export async function writeProgramManifest(options) {
  const { programId, runId, payload } = options
  const runDir = resolveProgramRunDir(programId, runId)

  const manifest = {
    generatedAtUtc: new Date().toISOString(),
    programId,
    runId,
    ...payload
  }

  const manifestPath = path.join(runDir, "manifest.json")
  await writeJsonFile(manifestPath, manifest)

  return {
    manifestPath: toRelativeFromArtifacts(manifestPath),
    manifest
  }
}

export function summarizeRenderResults(sequenceResults) {
  const totalFrames = sequenceResults.reduce((sum, item) => sum + item.captureCount, 0)
  const warningCount = sequenceResults.reduce((sum, item) => sum + (item.warnings?.length ?? 0), 0)

  return {
    sequenceCount: sequenceResults.length,
    totalFrames,
    warningCount,
    acceptedCount: sequenceResults.filter((entry) => entry.status === "accepted").length,
    rejectedCount: sequenceResults.filter((entry) => entry.status === "rejected").length,
    pendingCount: sequenceResults.filter((entry) => entry.status === "pending").length
  }
}
