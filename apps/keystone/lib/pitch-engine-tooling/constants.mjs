import path from "node:path"

export const REPO_ARTIFACTS_ROOT = path.resolve("F:/repos/hitech-os/artifacts")

export const PITCH_ARTIFACT_ROOT = path.join(REPO_ARTIFACTS_ROOT, "keystone-pitch-engine")
export const SCENE_ARTIFACT_ROOT = path.join(REPO_ARTIFACTS_ROOT, "keystone-scene-studio")
export const PITCH_BASELINE_ROOT = path.join(PITCH_ARTIFACT_ROOT, "baselines")

export const PITCH_PROGRAMS_DIR = "programs"
export const PITCH_RUNS_PER_PROGRAM_DEFAULT = 20
export const SCENE_RUNS_PER_OWNER_DEFAULT = 20

export const PITCH_SEQUENCE_DIR = "sequences"
export const PITCH_SCENE_DIR = "scenes"
export const PITCH_FRAMES_DIR = "frames"
export const PLAYER_DIR = "player"
export const LOG_DIR = "logs"

export const PITCH_REPORT_JSON = "report.json"
export const PITCH_REPORT_MD = "report.md"
export const PITCH_DIFF_NOTES = "DIFF_NOTES.md"
export const PITCH_SEQUENCE_TIMELINE_JSON = "timeline.json"
export const PITCH_RESOLVED_PROGRAM_JSON = "resolved-program.json"

export const SCENE_INDEX_JSON = "index.json"
export const SCENE_INDEX_MD = "index.md"
export const SCENE_INDEX_HTML = "index.html"

export const PITCH_INDEX_JSON = "index.json"
export const PITCH_INDEX_MD = "index.md"
export const PITCH_INDEX_HTML = "index.html"

export const PITCH_LAST_DOD_JSON = path.join(PITCH_ARTIFACT_ROOT, "last_dod.json")

export const ACCEPTED_STATUS = "accepted"
export const REJECTED_STATUS = "rejected"
export const PENDING_STATUS = "pending"

export const CAPTURE_TIMESTAMP_DEFAULTS_MS = Object.freeze([
  0,
  400,
  800,
  1200,
  1600,
  2000,
  2400,
  2800,
  3200,
  3600,
  4000,
  4400,
  4800,
  5200,
  5600,
  6000,
  6400,
  6800,
  7200,
  7600,
  8000
])

export const CAPTURE_MARKERS = Object.freeze([
  { id: "marker-start", tMs: 0, kind: "entry" },
  { id: "marker-narrative-shift", tMs: 2000, kind: "story" },
  { id: "marker-pivot", tMs: 4000, kind: "story" },
  { id: "marker-cta", tMs: 6000, kind: "decision" },
  { id: "marker-end", tMs: 8000, kind: "exit" }
])

export const PLAYWRIGHT_PACKAGE_SPEC = "playwright@1.51.1"
export const PLAYWRIGHT_CLI_TIMEOUT_MS = 10 * 60 * 1000

export const VIEWPORT_PRESETS = Object.freeze({
  desktop: Object.freeze({ width: 1440, height: 900, name: "desktop-1440x900" }),
  presenter: Object.freeze({ width: 1920, height: 1080, name: "presenter-1920x1080" }),
  laptop: Object.freeze({ width: 1366, height: 768, name: "laptop-1366x768" }),
  tablet: Object.freeze({ width: 1024, height: 768, name: "tablet-1024x768" }),
  mobile: Object.freeze({ width: 430, height: 932, name: "mobile-430x932" })
})

export const DEFAULT_VIEWPORT_KEY = "desktop"

export const PERFORMANCE_PROFILES = Object.freeze({
  full: Object.freeze({
    name: "full",
    frameSettleMs: 220,
    sceneReadyTimeoutMs: 5000,
    postGotoWaitMs: 80,
    markerMultiplier: 1,
    includeIntermediates: true
  }),
  smoke: Object.freeze({
    name: "smoke",
    frameSettleMs: 120,
    sceneReadyTimeoutMs: 3000,
    postGotoWaitMs: 50,
    markerMultiplier: 1,
    includeIntermediates: false
  }),
  lite: Object.freeze({
    name: "lite",
    frameSettleMs: 80,
    sceneReadyTimeoutMs: 1500,
    postGotoWaitMs: 30,
    markerMultiplier: 2,
    includeIntermediates: false
  })
})

export const DEFAULT_PERFORMANCE_PROFILE = PERFORMANCE_PROFILES.full

export const CANONICAL_TIMELINE_VERSION = "1.0.0"
export const SCENE_SCHEMA_VERSION = "1.0.0"

export const TRIAGE_GUARDRAILS = Object.freeze({
  requireRunDirectory: true,
  requireSequenceDirectory: true,
  requireDecisionReason: false,
  maxNoteLength: 4000,
  maxActorLength: 120,
  noteHeading: "# Diff Notes",
  noteSectionPrefix: "##",
  noteTimestampPrefix: "Timestamp:",
  noteActorPrefix: "Actor:",
  noteTextPrefix: "Note:"
})

export const RETENTION_POLICY_DEFAULT = Object.freeze({
  keepLast: PITCH_RUNS_PER_PROGRAM_DEFAULT,
  pinMarker: "PIN.marker",
  decisionFileName: "triage.json",
  allowPrunePinned: false,
  keepFailedRuns: true,
  maxPruneBatch: 100
})

export const TIMELINE_PLACEHOLDER_EVENTS = Object.freeze([
  { id: "intro", startMs: 0, endMs: 1200, description: "Context and premise" },
  { id: "evidence", startMs: 1200, endMs: 3200, description: "Operational proof points" },
  { id: "leverage", startMs: 3200, endMs: 5200, description: "Platform leverage and moat" },
  { id: "economics", startMs: 5200, endMs: 7200, description: "Economics and valuation" },
  { id: "close", startMs: 7200, endMs: 8000, description: "Decision frame and CTA" }
])

export const DOD_CHECK_STATUS = Object.freeze({
  pass: "PASS",
  fail: "FAIL",
  skip: "SKIP",
  warn: "WARN"
})

export const DOD_CHECKLIST_FILE = "tools/hos/quality/dod/PITCH_ENGINE_DOD_CHECKLIST.json"

export const DOD_CHECK_IDS = Object.freeze({
  layerDomContract: "layer-dom-contract",
  sceneReadySignal: "scene-ready-signal",
  schemaVersioned: "scene-schema-versioned-runtime-validation",
  routeDiscoveryOutput: "route-discovery-output",
  devOnly404Prod: "dev-only-404-in-prod",
  deterministicRunnerCommands: "deterministic-runner-commands",
  artifactsIndexExists: "artifacts-index-exists",
  retentionPinPresent: "retention-pin-present",
  claimWorkflowGate: "claim-workflow-governance-gate",
  capabilitiesRegistry: "capabilities-registry-prod-off",
  directorTimelineSequence: "director-timeline-sequence-keyframes",
  testsPresentAndPassing: "tests-exist-and-pass",
  doctorCommandPresent: "doctor-command-present",
  oneButtonRunnerPresent: "one-button-runner-present",
  playerOfflineStatic: "player-offline-static",
  diffNotesPresence: "diff-notes-presence",
  perSequenceReports: "per-sequence-reports",
  runRetentionInvariant: "run-retention-invariant"
})

export const SAFE_AUTOFIX_IDS = Object.freeze({
  regenerateIndexes: "autofix-regenerate-indexes",
  normalizeArtifactsIndex: "autofix-normalize-artifacts-index",
  normalizeNames: "autofix-normalize-names",
  regenRouteDiscoveryOutputs: "autofix-regenerate-route-discovery"
})

export const RENDER_LOG_FILE = "console.log"

export const OFFLINE_PLAYER_FILES = Object.freeze([
  "index.html",
  "player.js",
  "styles.css"
])

export const RUN_MODE = Object.freeze({
  smoke: "smoke",
  full: "full",
  update: "update"
})

export const SEQUENCE_DECISION_FILE = "triage.json"
export const SCENE_DECISION_FILE = "triage.json"

export const TRIAGE_STATUS_VALUES = Object.freeze([
  ACCEPTED_STATUS,
  REJECTED_STATUS,
  PENDING_STATUS
])

export const INDEX_METADATA_VERSION = "1.0.0"

export const SCENE_OPERATIONS = Object.freeze({
  triageDir: "triage",
  retentionDir: "retention",
  decisionsDir: "decisions",
  notesDir: "notes",
  rerunDir: "rerun-requests"
})

export const DOCTOR_CHECKS = Object.freeze([
  "node",
  "pnpm",
  "playwright-cli",
  "playwright-browser",
  "port-3100",
  "artifact-root",
  "write-permission",
  "path-safety"
])

export const WINDOW_SAFE_FILENAME_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/
export const SAFE_ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/

export const ROUTE_HINTS = Object.freeze({
  pitchHome: "/pitch",
  programBase: "/pitch",
  fallbackReadySelector: "body"
})

export const CAPTURE_QUERY_FLAGS = Object.freeze({
  reducedMotion: "peReducedMotion",
  deterministic: "peDeterministic",
  timestamp: "peTime",
  profile: "peProfile"
})

export const INDEX_LINK_LIMIT = 100

export const REPORT_SECTIONS = Object.freeze([
  "summary",
  "capture",
  "diff",
  "retention",
  "timeline",
  "notes",
  "decisions",
  "warnings",
  "invariants"
])

export const TERMINAL_SYMBOLS = Object.freeze({
  pass: "[PASS]",
  fail: "[FAIL]",
  warn: "[WARN]",
  info: "[INFO]"
})

export const DETERMINISTIC_CLOCK_REFERENCE = "1970-01-01T00:00:00.000Z"

export const DEFAULT_SCENE_OWNER = "scene-studio"
export const DEFAULT_PITCH_OWNER = "pitch-engine"

export const DOC_PATHS = Object.freeze({
  pitchTooling: "docs/quality/PITCH_ENGINE_TOOLING.md",
  sceneOperations: "docs/quality/SCENE_STUDIO_OPERATIONS.md"
})

export const TASK_BUNDLE_ROOT = path.join(
  "tools",
  "codex",
  "runs",
  "20260304_061005_61C9",
  "B_tooling"
)

export const TASK_BUNDLE_FILES = Object.freeze([
  "STATUS.json",
  "SUMMARY.md",
  "FILES_CHANGED.json",
  "DIFF.patch",
  "SUGGESTIONS.md",
  "SCOPE_LOCK.json",
  "HANDOFF_NOTE.json",
  "LOGS/INDEX.json",
  "CODEX_OUTPUT.txt",
  "SELF_EVAL_REPORT.json",
  "SANCTION_SCORE.json",
  "SELF_CORRECTION_LOG.jsonl",
  "LOC_REPORT.md",
  "DOD_RESULTS.json"
])

export const DONE_MARKER_PATH = path.join(TASK_BUNDLE_ROOT, "DONE.marker")

export const DOCTOR_LOG_FILE = path.join(LOG_DIR, "doctor.log")

export const PSEUDO_PNG_BASE64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGD4DwABBAEAH2wL4QAAAABJRU5ErkJggg=="
