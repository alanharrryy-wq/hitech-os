import type {
  AgentCapabilities,
  HealthReport,
  JobRequest,
  JobResult,
  PitchDeck,
  PitchScreen,
  PitchScreenSlug
} from "../index.js";
import {
  CONTRACT_VERSION_INFO,
  FEATURE_FLAGS_DEFAULTS,
  PITCH_DECK_FIXTURE,
  PITCH_SCREEN_FIXTURES,
  PITCH_SCREEN_ORDER
} from "../index.js";

const _jobRequestSample: JobRequest = {
  jobId: "job-check-001",
  kind: "echo",
  input: { text: "ok" },
  requestedAtUtc: "2026-01-01T00:00:00.000Z",
  flags: FEATURE_FLAGS_DEFAULTS
};

const _jobResultSample: JobResult = {
  jobId: _jobRequestSample.jobId,
  kind: _jobRequestSample.kind,
  status: "queued",
  output: {},
  logs: [],
  finishedAtUtc: null
};

const _capabilitiesSample: AgentCapabilities = {
  serviceName: "ai-agent",
  version: "0.2.0",
  protocolVersion: CONTRACT_VERSION_INFO.protocolVersion,
  deterministic: true,
  supportedJobKinds: ["echo"],
  maxInputChars: 1,
  defaults: FEATURE_FLAGS_DEFAULTS,
  notes: ["deterministic"]
};

const _healthSample: HealthReport = {
  service: "core-api",
  version: "0.2.0",
  contractVersion: CONTRACT_VERSION_INFO.protocolVersion,
  status: "ok",
  timestampUtc: "2026-01-01T00:00:00.000Z",
  checks: [{ name: "contracts", status: "ok", message: "ok" }]
};

const _pitchDeckSample: PitchDeck = PITCH_DECK_FIXTURE;
const _pitchSlugSample: PitchScreenSlug = PITCH_SCREEN_ORDER[0] ?? "01-double-engine";
const _pitchScreenSample: PitchScreen = PITCH_SCREEN_FIXTURES[_pitchSlugSample];

void [
  _jobRequestSample,
  _jobResultSample,
  _capabilitiesSample,
  _healthSample,
  _pitchDeckSample,
  _pitchSlugSample,
  _pitchScreenSample
];
