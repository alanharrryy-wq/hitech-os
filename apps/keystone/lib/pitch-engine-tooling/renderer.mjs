import path from "node:path"
import {
  PITCH_DIFF_NOTES,
  PITCH_PROGRAMS_DIR,
  PITCH_REPORT_JSON,
  PITCH_REPORT_MD,
  PITCH_RUNS_PER_PROGRAM_DEFAULT,
  PENDING_STATUS,
  PITCH_RESOLVED_PROGRAM_JSON,
  PITCH_SEQUENCE_TIMELINE_JSON,
  RENDER_LOG_FILE,
  RUN_MODE
} from "./constants.mjs"
import { resolveCapturePlan } from "./capture-plan.mjs"
import { stableHash } from "./deterministic.mjs"
import { runDoctor } from "./doctor.mjs"
import { ensureDir, ensureDirSync, readJsonIfExists, touchFile, writeJsonFile, writeTextFile } from "./fs-utils.mjs"
import { buildSceneDiffAssets } from "./image-utils.mjs"
import { writePitchIndexFiles, writeSceneIndexFiles } from "./indexer.mjs"
import { createLogger } from "./logger.mjs"
import { resolvePerformanceProfile, profileToReportEntry } from "./perf-profile.mjs"
import {
  resolveProgram,
  resolveSequence,
  buildSceneSchemaEnvelope,
  ensureCanonicalProgram
} from "./program-model.mjs"
import {
  resolveBaselineSceneDir,
  resolveProgramConsoleLogPath,
  resolveProgramResolvedPath,
  resolveProgramRunDir,
  resolveProgramTimelinePath,
  resolveSceneDir,
  resolveSceneSnapshotPath,
  resolveSequenceDir,
  resolveSequenceFramesDir,
  toRelativeFromArtifacts
} from "./paths.mjs"
import { generateOfflinePlayer } from "./player.mjs"
import { runPlaywrightCapture, fallbackCapture } from "./playwright-harness.mjs"
import { writeProgramManifest, writeSceneReport, writeSequenceReport } from "./reports.mjs"
import { pruneProgramRuns } from "./retention.mjs"
import { markSequencePending } from "./triage.mjs"
import { buildProgramTimeline, flattenTimelineCaptures } from "./timeline.mjs"
import { buildTimestampFileName, sanitizeId } from "./windows-safe.mjs"

async function canReachRenderTarget(baseUrl) {
  const timeoutMs = 1200
  const controller = new AbortController()
  const timeoutHandle = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const healthUrl = new URL("/", baseUrl)
    const response = await fetch(healthUrl, {
      method: "GET",
      signal: controller.signal
    })
    return response.ok || response.status === 404
  } catch {
    return false
  } finally {
    clearTimeout(timeoutHandle)
  }
}

function makeRunId(inputRunId) {
  if (typeof inputRunId === "string" && inputRunId.length > 0) {
    return sanitizeId(inputRunId)
  }

  const now = new Date()
  const y = now.getUTCFullYear()
  const m = String(now.getUTCMonth() + 1).padStart(2, "0")
  const d = String(now.getUTCDate()).padStart(2, "0")
  const hh = String(now.getUTCHours()).padStart(2, "0")
  const mm = String(now.getUTCMinutes()).padStart(2, "0")
  const ss = String(now.getUTCSeconds()).padStart(2, "0")
  const suffix = Math.random().toString(36).slice(2, 6).toUpperCase()
  return `${y}${m}${d}_${hh}${mm}${ss}_${suffix}`
}

function buildCaptureTasks(program, timeline, programId, runId) {
  const tasks = []

  for (const sequenceTimeline of timeline.sequences) {
    const framesDir = resolveSequenceFramesDir(programId, runId, sequenceTimeline.sequenceId)

    for (const tMs of sequenceTimeline.timestampsMs) {
      const fileName = buildTimestampFileName(tMs)
      const marker = sequenceTimeline.markers.find((entry) => entry.tMs === tMs)
      tasks.push({
        programId,
        runId,
        sequenceId: sequenceTimeline.sequenceId,
        sceneId: sequenceTimeline.sceneId,
        route: sequenceTimeline.route,
        tMs,
        marker: marker?.id ?? null,
        outputPath: path.join(framesDir, fileName),
        markerOutputPath: marker ? path.join(framesDir, `${marker.id}.png`) : null
      })
    }
  }

  return tasks
}

function groupBySequence(items) {
  const grouped = new Map()

  for (const item of items) {
    const key = item.sequenceId
    if (!grouped.has(key)) {
      grouped.set(key, [])
    }
    grouped.get(key).push(item)
  }

  for (const [, values] of grouped.entries()) {
    values.sort((a, b) => a.tMs - b.tMs)
  }

  return grouped
}

async function writeSequenceArtifacts(context) {
  const {
    programId,
    runId,
    sequence,
    captures,
    profileDecision,
    sharedWarnings
  } = context

  const sequenceDir = resolveSequenceDir(programId, runId, sequence.sequenceId)
  await ensureDir(sequenceDir)

  const notesPath = path.join(sequenceDir, PITCH_DIFF_NOTES)
  const notePayload = `# Diff Notes\n\nInitial notes for sequence ${sequence.sequenceId}.\n`
  await touchFile(notesPath, notePayload)

  await markSequencePending({
    programId,
    runId,
    sequenceId: sequence.sequenceId,
    actor: "renderer"
  })

  const profileReport = profileToReportEntry(profileDecision)

  const reportPayload = {
    route: sequence.route,
    captureCount: captures.length,
    profile: profileReport,
    status: PENDING_STATUS,
    warnings: [...sharedWarnings],
    frames: captures.map((capture) => ({
      tMs: capture.tMs,
      file: path.basename(capture.outputPath),
      marker: capture.marker ?? null,
      sceneReadyDetected: capture.sceneReadyDetected,
      strategy: capture.strategy
    })),
    schemaEnvelope: buildSceneSchemaEnvelope(programId, runId, sequence)
  }

  const reportPaths = await writeSequenceReport({
    programId,
    runId,
    sequenceId: sequence.sequenceId,
    payload: reportPayload
  })

  return {
    sequenceId: sequence.sequenceId,
    sceneId: sequence.sceneId,
    route: sequence.route,
    captureCount: captures.length,
    warnings: sharedWarnings,
    status: PENDING_STATUS,
    reportPaths,
    notesPath: toRelativeFromArtifacts(notesPath)
  }
}

async function writeSceneArtifacts(context) {
  const { programId, runId, sequence, captures, warnings } = context
  const sceneDir = resolveSceneDir(programId, runId, sequence.sceneId)
  await ensureDir(sceneDir)

  const latestCapture = captures[captures.length - 1]
  const baselineSceneDir = resolveBaselineSceneDir(programId, sequence.sceneId)
  const baselineImagePath = path.join(baselineSceneDir, "latest.png")

  const beforePath = resolveSceneSnapshotPath(programId, runId, sequence.sceneId, "before")
  const afterPath = resolveSceneSnapshotPath(programId, runId, sequence.sceneId, "after")
  const diffPath = resolveSceneSnapshotPath(programId, runId, sequence.sceneId, "diff")
  const diffMetaPath = path.join(sceneDir, "diff-meta.json")

  const diffAssets = await buildSceneDiffAssets({
    baselinePath: baselineImagePath,
    currentPath: latestCapture.outputPath,
    beforeOutputPath: beforePath,
    afterOutputPath: afterPath,
    diffOutputPath: diffPath,
    metadataOutputPath: diffMetaPath
  })

  const notesPath = path.join(sceneDir, PITCH_DIFF_NOTES)
  const notesText = `# Diff Notes\n\nInitial notes for scene ${sequence.sceneId}.\n`
  await touchFile(notesPath, notesText)

  const reportPayload = {
    beforeImage: path.basename(beforePath),
    afterImage: path.basename(afterPath),
    diffImage: path.basename(diffPath),
    baselineExists: diffAssets.baselineExists,
    status: PENDING_STATUS,
    warnings
  }

  const reportPaths = await writeSceneReport({
    programId,
    runId,
    sceneId: sequence.sceneId,
    payload: reportPayload
  })

  return {
    sceneId: sequence.sceneId,
    baselineExists: diffAssets.baselineExists,
    reportPaths,
    notesPath: toRelativeFromArtifacts(notesPath),
    before: toRelativeFromArtifacts(beforePath),
    after: toRelativeFromArtifacts(afterPath),
    diff: toRelativeFromArtifacts(diffPath)
  }
}

async function writeTopLevelArtifacts(context) {
  const {
    program,
    programId,
    runId,
    mode,
    profileDecision,
    timeline,
    sequenceSummaries,
    sceneSummaries,
    warnings,
    captureStrategy,
    runDir
  } = context

  const resolvedProgramPath = resolveProgramResolvedPath(programId, runId)
  const timelinePath = resolveProgramTimelinePath(programId, runId)

  await writeJsonFile(resolvedProgramPath, {
    ...program,
    mode,
    captureStrategy
  })

  await writeJsonFile(timelinePath, timeline)

  const programReportJsonPath = path.join(runDir, PITCH_REPORT_JSON)
  const programReportMdPath = path.join(runDir, PITCH_REPORT_MD)

  const summary = {
    programId,
    runId,
    mode,
    profile: profileToReportEntry(profileDecision),
    sequenceCount: sequenceSummaries.length,
    sceneCount: sceneSummaries.length,
    warnings,
    generatedAtUtc: new Date().toISOString(),
    hash: stableHash({
      programId,
      runId,
      mode,
      profile: profileDecision.actual.name,
      timelineHash: timeline.hash,
      sequenceCount: sequenceSummaries.length
    }),
    sequenceSummaries,
    sceneSummaries
  }

  await writeJsonFile(programReportJsonPath, summary)

  const mdLines = [
    `# Program Report ${programId}`,
    "",
    `Run: \`${runId}\``,
    `Mode: ${mode}`,
    `Profile: ${profileDecision.actual.name}`,
    `Degraded: ${profileDecision.degraded}`,
    `Capture strategy: ${captureStrategy}`,
    `Generated: ${summary.generatedAtUtc}`,
    "",
    "## Sequences",
    ...sequenceSummaries.map((entry) =>
      `- ${entry.sequenceId} | captures=${entry.captureCount} | status=${entry.status}`
    ),
    "",
    "## Scenes",
    ...sceneSummaries.map((entry) =>
      `- ${entry.sceneId} | baselineExists=${entry.baselineExists}`
    ),
    "",
    "## Warnings",
    ...(warnings.length > 0 ? warnings.map((warning) => `- ${warning}`) : ["- none"]),
    ""
  ]

  await writeTextFile(programReportMdPath, mdLines.join("\n") + "\n")

  await writeProgramManifest({
    programId,
    runId,
    payload: {
      mode,
      profile: profileToReportEntry(profileDecision),
      captureStrategy,
      warnings,
      files: {
        resolvedProgram: toRelativeFromArtifacts(resolvedProgramPath),
        timeline: toRelativeFromArtifacts(timelinePath),
        reportJson: toRelativeFromArtifacts(programReportJsonPath),
        reportMd: toRelativeFromArtifacts(programReportMdPath)
      }
    }
  })

  return summary
}

export async function renderProgram(options = {}) {
  const programId = sanitizeId(options.programId ?? "hitech-pitch")
  const runId = makeRunId(options.runId)
  const mode = options.mode ?? RUN_MODE.full
  const keepLast = Number.isInteger(options.keepLast) ? options.keepLast : PITCH_RUNS_PER_PROGRAM_DEFAULT

  const runDir = resolveProgramRunDir(programId, runId)
  const logsPath = resolveProgramConsoleLogPath(programId, runId)
  ensureDirSync(path.dirname(logsPath))

  const logger = createLogger({
    prefix: `render:${programId}:${runId}`,
    logFile: logsPath
  })

  logger.info("Starting render", { programId, runId, mode })

  const doctor = await runDoctor({
    cwd: options.repoRoot ?? process.cwd(),
    skipBrowserInstall: options.skipBrowserInstall === true,
    logFile: logsPath,
    prefix: `doctor:${programId}`
  })

  if (!doctor.ok && options.allowDoctorFail !== true) {
    throw new Error("Doctor checks failed. Use --allow-doctor-fail to continue with placeholder capture.")
  }

  const program = ensureCanonicalProgram(resolveProgram(programId))
  const profileDecision = resolvePerformanceProfile(
    {
      mode,
      smoke: mode === "smoke",
      full: mode === "full"
    },
    {
      forceLite: options.forceLite === true
    }
  )

  const capturePlan = await resolveCapturePlan(program, mode, options.repoRoot ?? process.cwd())
  const timeline = buildProgramTimeline(program, capturePlan, profileDecision.actual)
  const tasks = buildCaptureTasks(program, timeline, programId, runId)

  for (const task of tasks) {
    await ensureDir(path.dirname(task.outputPath))
  }

  const captureJob = {
    runId,
    programId,
    mode,
    viewport: options.viewport ?? { width: 1440, height: 900 },
    profile: profileDecision.actual,
    navigationTimeoutMs: Math.max(2_500, Number(profileDecision.actual.sceneReadyTimeoutMs ?? 5_000) + 1_500),
    tempDir: runDir,
    tasks
  }

  let capturePayload = null
  const baseUrl = options.baseUrl ?? "http://127.0.0.1:3100"
  const targetReachable = await canReachRenderTarget(baseUrl)

  if (!targetReachable) {
    logger.warn(
      `Render target ${baseUrl} is unreachable. Skipping Playwright and using placeholder captures.`
    )
    capturePayload = await fallbackCapture(captureJob)
  } else {
    const captureResult = await runPlaywrightCapture(captureJob, {
      cwd: options.repoRoot ?? process.cwd()
    })

    capturePayload = captureResult.payload

    if (!captureResult.ok || !Array.isArray(capturePayload.captures) || capturePayload.captures.length === 0) {
      logger.warn("Playwright capture failed or empty. Falling back to placeholder strategy.")
      capturePayload = await fallbackCapture(captureJob)
    }
  }

  const captureWarnings = [...(capturePayload.warnings ?? [])]
  const groupedCaptures = groupBySequence(capturePayload.captures)

  const sequenceSummaries = []
  const sceneSummaries = []

  for (const sequence of program.sequences) {
    const sequenceCaptures = groupedCaptures.get(sequence.sequenceId) ?? []
    const sequenceWarnings = [...captureWarnings]

    if (sequenceCaptures.length === 0) {
      sequenceWarnings.push(`No captures generated for ${sequence.sequenceId}.`)
    }

    const sequenceSummary = await writeSequenceArtifacts({
      programId,
      runId,
      sequence,
      captures: sequenceCaptures,
      profileDecision,
      sharedWarnings: sequenceWarnings
    })

    sequenceSummaries.push(sequenceSummary)

    if (sequenceCaptures.length > 0) {
      const sceneSummary = await writeSceneArtifacts({
        programId,
        runId,
        sequence,
        captures: sequenceCaptures,
        warnings: sequenceWarnings
      })
      sceneSummaries.push(sceneSummary)
    }
  }

  await generateOfflinePlayer(programId, runId, timeline)

  const summary = await writeTopLevelArtifacts({
    program,
    programId,
    runId,
    mode,
    profileDecision,
    timeline,
    sequenceSummaries,
    sceneSummaries,
    warnings: captureWarnings,
    captureStrategy: capturePayload.strategy ?? "unknown",
    runDir
  })

  const prune = await pruneProgramRuns(programId, {
    keepLast
  })

  await writePitchIndexFiles()
  await writeSceneIndexFiles()

  logger.pass("Render completed", {
    programId,
    runId,
    sequenceCount: sequenceSummaries.length,
    captureCount: flattenTimelineCaptures(timeline).length,
    strategy: capturePayload.strategy,
    retention: prune.counts
  })

  return {
    programId,
    runId,
    runDir: toRelativeFromArtifacts(runDir),
    mode,
    profile: profileDecision,
    summary,
    sequenceSummaries,
    sceneSummaries,
    retention: prune,
    captureWarnings,
    doctor,
    capture: {
      strategy: capturePayload.strategy,
      count: capturePayload.captures.length,
      warnings: captureWarnings
    }
  }
}

export async function renderSingleSequence(options = {}) {
  const { programId, sequenceId } = options
  const normalizedProgramId = sanitizeId(programId ?? "hitech-pitch")
  const runResult = await renderProgram({
    ...options,
    programId: normalizedProgramId
  })

  const sequence = resolveSequence(resolveProgram(normalizedProgramId), sequenceId)
  const selected = runResult.sequenceSummaries.find((entry) => entry.sequenceId === sequence.sequenceId)

  if (!selected) {
    throw new Error(`Sequence was not rendered: ${sequence.sequenceId}`)
  }

  return {
    ...runResult,
    selectedSequence: selected
  }
}
