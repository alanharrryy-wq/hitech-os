import path from "node:path"
import {
  LOG_DIR,
  PITCH_ARTIFACT_ROOT,
  PITCH_BASELINE_ROOT,
  PITCH_FRAMES_DIR,
  PITCH_PROGRAMS_DIR,
  PITCH_SCENE_DIR,
  PITCH_SEQUENCE_DIR,
  PLAYER_DIR,
  REPO_ARTIFACTS_ROOT,
  SCENE_ARTIFACT_ROOT,
  SCENE_OPERATIONS,
  SEQUENCE_DECISION_FILE
} from "./constants.mjs"
import { sanitizeId, safeJoin } from "./windows-safe.mjs"

export function resolveRepoArtifactsRoot() {
  return REPO_ARTIFACTS_ROOT
}

export function resolvePitchArtifactsRoot() {
  return PITCH_ARTIFACT_ROOT
}

export function resolveSceneArtifactsRoot() {
  return SCENE_ARTIFACT_ROOT
}

export function resolveProgramRunDir(programId, runId) {
  return safeJoin(PITCH_ARTIFACT_ROOT, PITCH_PROGRAMS_DIR, sanitizeId(programId), sanitizeId(runId))
}

export function resolveProgramDir(programId) {
  return safeJoin(PITCH_ARTIFACT_ROOT, PITCH_PROGRAMS_DIR, sanitizeId(programId))
}

export function resolveSequenceDir(programId, runId, sequenceId) {
  return safeJoin(
    resolveProgramRunDir(programId, runId),
    PITCH_SEQUENCE_DIR,
    sanitizeId(sequenceId)
  )
}

export function resolveSequenceFramesDir(programId, runId, sequenceId) {
  return safeJoin(resolveSequenceDir(programId, runId, sequenceId), PITCH_FRAMES_DIR)
}

export function resolveSceneDir(programId, runId, sceneId) {
  return safeJoin(resolveProgramRunDir(programId, runId), PITCH_SCENE_DIR, sanitizeId(sceneId))
}

export function resolveProgramLogsDir(programId, runId) {
  return safeJoin(resolveProgramRunDir(programId, runId), LOG_DIR)
}

export function resolvePlayerDir(programId, runId) {
  return safeJoin(resolveProgramRunDir(programId, runId), PLAYER_DIR)
}

export function resolveSequenceReportJsonPath(programId, runId, sequenceId) {
  return path.join(resolveSequenceDir(programId, runId, sequenceId), "report.json")
}

export function resolveSequenceReportMdPath(programId, runId, sequenceId) {
  return path.join(resolveSequenceDir(programId, runId, sequenceId), "report.md")
}

export function resolveSequenceNotesPath(programId, runId, sequenceId) {
  return path.join(resolveSequenceDir(programId, runId, sequenceId), "DIFF_NOTES.md")
}

export function resolveSequenceDecisionPath(programId, runId, sequenceId) {
  return path.join(resolveSequenceDir(programId, runId, sequenceId), SEQUENCE_DECISION_FILE)
}

export function resolveSceneReportJsonPath(programId, runId, sceneId) {
  return path.join(resolveSceneDir(programId, runId, sceneId), "report.json")
}

export function resolveSceneReportMdPath(programId, runId, sceneId) {
  return path.join(resolveSceneDir(programId, runId, sceneId), "report.md")
}

export function resolveSceneNotesPath(programId, runId, sceneId) {
  return path.join(resolveSceneDir(programId, runId, sceneId), "DIFF_NOTES.md")
}

export function resolveSceneDecisionPath(programId, runId, sceneId) {
  return path.join(resolveSceneDir(programId, runId, sceneId), "triage.json")
}

export function resolveSceneSnapshotPath(programId, runId, sceneId, kind) {
  return path.join(resolveSceneDir(programId, runId, sceneId), `${kind}.png`)
}

export function resolveBaselineSequenceDir(programId, sequenceId) {
  return safeJoin(PITCH_BASELINE_ROOT, "programs", sanitizeId(programId), "sequences", sanitizeId(sequenceId))
}

export function resolveBaselineSceneDir(programId, sceneId) {
  return safeJoin(PITCH_BASELINE_ROOT, "programs", sanitizeId(programId), "scenes", sanitizeId(sceneId))
}

export function resolvePitchIndexPath(fileName) {
  return path.join(PITCH_ARTIFACT_ROOT, fileName)
}

export function resolveSceneIndexPath(fileName) {
  return path.join(SCENE_ARTIFACT_ROOT, fileName)
}

export function resolvePitchDecisionLedgerPath(programId) {
  return path.join(resolveProgramDir(programId), "decisions.json")
}

export function resolvePitchRetentionMetadataPath(programId) {
  return path.join(resolveProgramDir(programId), "retention.json")
}

export function resolveSceneOperationDir(segment) {
  return safeJoin(SCENE_ARTIFACT_ROOT, segment)
}

export function resolveSceneOperationFile(segment, fileName) {
  return path.join(resolveSceneOperationDir(segment), fileName)
}

export function resolveSceneTriageDir() {
  return resolveSceneOperationDir(SCENE_OPERATIONS.triageDir)
}

export function resolveSceneRetentionDir() {
  return resolveSceneOperationDir(SCENE_OPERATIONS.retentionDir)
}

export function resolveSceneDecisionsDir() {
  return resolveSceneOperationDir(SCENE_OPERATIONS.decisionsDir)
}

export function resolveSceneNotesDir() {
  return resolveSceneOperationDir(SCENE_OPERATIONS.notesDir)
}

export function resolveSceneRerunDir() {
  return resolveSceneOperationDir(SCENE_OPERATIONS.rerunDir)
}

export function resolveSceneDecisionFile(sceneId, runId) {
  return path.join(resolveSceneDecisionsDir(), `${sanitizeId(sceneId)}--${sanitizeId(runId)}.json`)
}

export function resolveSceneNotesFile(sceneId, runId) {
  return path.join(resolveSceneNotesDir(), `${sanitizeId(sceneId)}--${sanitizeId(runId)}.md`)
}

export function resolveSceneRerunFile(sceneId) {
  return path.join(resolveSceneRerunDir(), `${sanitizeId(sceneId)}.json`)
}

export function resolveProgramTimelinePath(programId, runId) {
  return path.join(resolveProgramRunDir(programId, runId), "timeline.json")
}

export function resolveProgramResolvedPath(programId, runId) {
  return path.join(resolveProgramRunDir(programId, runId), "resolved-program.json")
}

export function resolveProgramConsoleLogPath(programId, runId) {
  return path.join(resolveProgramLogsDir(programId, runId), "console.log")
}

export function resolveProgramPlayerAssetPath(programId, runId, assetName) {
  return path.join(resolvePlayerDir(programId, runId), assetName)
}

export function resolvePitchProgramsRoot() {
  return path.join(PITCH_ARTIFACT_ROOT, PITCH_PROGRAMS_DIR)
}

export function resolveSharedRetentionPath() {
  return path.join(PITCH_ARTIFACT_ROOT, "retention")
}

export function resolveRunPinMarkerPath(programId, runId) {
  return path.join(resolveProgramRunDir(programId, runId), "PIN.marker")
}

export function resolveProgramManifestPath(programId, runId) {
  return path.join(resolveProgramRunDir(programId, runId), "manifest.json")
}

export function toRelativeFromArtifacts(absolutePath) {
  const root = path.resolve(REPO_ARTIFACTS_ROOT)
  const target = path.resolve(absolutePath)
  if (target.toLowerCase().startsWith(root.toLowerCase())) {
    const relative = path.relative(root, target)
    return relative.replace(/\\/g, "/")
  }

  return target.replace(/\\/g, "/")
}
