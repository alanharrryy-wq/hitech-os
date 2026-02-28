import { RunSummary, RunSummarySchema } from "../mission-control/run.js";
import { parseOrThrow } from "../parsing.js";

const BASE_TIMESTAMPS = {
  createdAt: "2026-02-01T08:00:00.000Z",
  scheduledAt: "2026-02-01T08:05:00.000Z",
  startedAt: "2026-02-01T08:07:00.000Z",
  updatedAt: "2026-02-01T08:12:00.000Z",
  finishedAt: null
} as const;

export const RUN_FIXTURES: readonly RunSummary[] = [
  {
    id: "run_alpha-001",
    name: "Alpha Build Validation",
    status: "running",
    priority: "high",
    source: "manual",
    ownerId: "usr_ops-0001",
    assigneeId: "usr_ops-0002",
    widgetIds: ["wid_stat-001", "wid_table-001", "wid_feed-001"],
    health: "healthy",
    progress: { currentStep: 4, totalSteps: 10, percent: 40, etaSeconds: 720 },
    tags: ["build", "alpha", "validation"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      updatedAt: "2026-02-15T08:12:00.000Z"
    },
    version: 3
  },
  {
    id: "run_bravo-002",
    name: "Bravo Regression Suite",
    status: "queued",
    priority: "normal",
    source: "schedule",
    ownerId: "usr_ops-0003",
    assigneeId: null,
    widgetIds: ["wid_table-001", "wid_feed-001"],
    health: "unknown",
    progress: { currentStep: 0, totalSteps: 12, percent: 0, etaSeconds: null },
    tags: ["regression", "nightly"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-15T07:55:00.000Z",
      scheduledAt: "2026-02-15T09:00:00.000Z",
      startedAt: null,
      updatedAt: "2026-02-15T08:00:00.000Z"
    },
    version: 1
  },
  {
    id: "run_charlie-003",
    name: "Charlie Security Hardening",
    status: "paused",
    priority: "critical",
    source: "api",
    ownerId: "usr_sec-0001",
    assigneeId: "usr_sec-0001",
    widgetIds: ["wid_dial-001", "wid_chart-001", "wid_feed-001"],
    health: "degraded",
    progress: { currentStep: 7, totalSteps: 15, percent: 46.6, etaSeconds: 2200 },
    tags: ["security", "hardening"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-14T10:00:00.000Z",
      startedAt: "2026-02-14T10:20:00.000Z",
      updatedAt: "2026-02-15T05:15:00.000Z"
    },
    version: 12
  },
  {
    id: "run_delta-004",
    name: "Delta Data Backfill",
    status: "succeeded",
    priority: "normal",
    source: "automation",
    ownerId: "usr_data-0001",
    assigneeId: "usr_data-0002",
    widgetIds: ["wid_stat-002", "wid_table-002"],
    health: "healthy",
    progress: { currentStep: 20, totalSteps: 20, percent: 100, etaSeconds: 0 },
    tags: ["backfill", "etl", "finance"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-13T18:00:00.000Z",
      startedAt: "2026-02-13T18:04:00.000Z",
      updatedAt: "2026-02-13T18:44:00.000Z",
      finishedAt: "2026-02-13T18:44:00.000Z"
    },
    version: 2
  },
  {
    id: "run_echo-005",
    name: "Echo API Contract Checks",
    status: "failed",
    priority: "high",
    source: "schedule",
    ownerId: "usr_api-0001",
    assigneeId: "usr_api-0003",
    widgetIds: ["wid_stat-003", "wid_feed-001", "wid_table-003"],
    health: "degraded",
    progress: { currentStep: 9, totalSteps: 12, percent: 75, etaSeconds: null },
    tags: ["api", "contracts", "blocking"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-12T03:00:00.000Z",
      startedAt: "2026-02-12T03:03:00.000Z",
      updatedAt: "2026-02-12T03:20:00.000Z",
      finishedAt: "2026-02-12T03:20:00.000Z"
    },
    version: 8
  },
  {
    id: "run_foxtrot-006",
    name: "Foxtrot Search Indexing",
    status: "running",
    priority: "normal",
    source: "automation",
    ownerId: "usr_search-0001",
    assigneeId: "usr_search-0002",
    widgetIds: ["wid_dial-002", "wid_table-004"],
    health: "healthy",
    progress: { currentStep: 3, totalSteps: 9, percent: 33.3, etaSeconds: 1800 },
    tags: ["index", "search"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-16T02:00:00.000Z",
      startedAt: "2026-02-16T02:03:00.000Z",
      updatedAt: "2026-02-16T02:18:00.000Z"
    },
    version: 5
  },
  {
    id: "run_golf-007",
    name: "Golf Billing Reconciliation",
    status: "scheduled",
    priority: "high",
    source: "schedule",
    ownerId: "usr_fin-0001",
    assigneeId: null,
    widgetIds: ["wid_stat-004", "wid_table-005"],
    health: "unknown",
    progress: { currentStep: 0, totalSteps: 14, percent: 0, etaSeconds: null },
    tags: ["billing", "finance"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-15T18:00:00.000Z",
      scheduledAt: "2026-02-16T06:00:00.000Z",
      startedAt: null,
      updatedAt: "2026-02-15T18:05:00.000Z"
    },
    version: 4
  },
  {
    id: "run_hotel-008",
    name: "Hotel Cache Warmup",
    status: "canceled",
    priority: "low",
    source: "manual",
    ownerId: "usr_platform-0001",
    assigneeId: "usr_platform-0002",
    widgetIds: ["wid_stat-005"],
    health: "degraded",
    progress: { currentStep: 1, totalSteps: 6, percent: 16.6, etaSeconds: null },
    tags: ["cache", "warmup"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-10T11:00:00.000Z",
      startedAt: "2026-02-10T11:06:00.000Z",
      updatedAt: "2026-02-10T11:12:00.000Z",
      finishedAt: "2026-02-10T11:12:00.000Z"
    },
    version: 2
  },
  {
    id: "run_india-009",
    name: "India Feature Matrix",
    status: "running",
    priority: "normal",
    source: "api",
    ownerId: "usr_pm-0001",
    assigneeId: "usr_ops-0001",
    widgetIds: ["wid_table-006", "wid_chart-002", "wid_feed-002"],
    health: "healthy",
    progress: { currentStep: 5, totalSteps: 8, percent: 62.5, etaSeconds: 600 },
    tags: ["feature", "matrix"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-16T01:00:00.000Z",
      startedAt: "2026-02-16T01:02:00.000Z",
      updatedAt: "2026-02-16T01:45:00.000Z"
    },
    version: 9
  },
  {
    id: "run_juliet-010",
    name: "Juliet Session Cleanup",
    status: "succeeded",
    priority: "low",
    source: "automation",
    ownerId: "usr_auth-0001",
    assigneeId: "usr_auth-0001",
    widgetIds: ["wid_stat-006", "wid_table-007"],
    health: "healthy",
    progress: { currentStep: 6, totalSteps: 6, percent: 100, etaSeconds: 0 },
    tags: ["cleanup", "auth"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-08T23:00:00.000Z",
      startedAt: "2026-02-08T23:01:00.000Z",
      updatedAt: "2026-02-08T23:07:00.000Z",
      finishedAt: "2026-02-08T23:07:00.000Z"
    },
    version: 1
  },
  {
    id: "run_kilo-011",
    name: "Kilo Message Queue Drain",
    status: "failed",
    priority: "critical",
    source: "automation",
    ownerId: "usr_queue-0001",
    assigneeId: "usr_queue-0003",
    widgetIds: ["wid_dial-003", "wid_feed-003", "wid_table-008"],
    health: "stalled",
    progress: { currentStep: 2, totalSteps: 18, percent: 11.1, etaSeconds: null },
    tags: ["queue", "outage", "critical"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-11T04:00:00.000Z",
      startedAt: "2026-02-11T04:05:00.000Z",
      updatedAt: "2026-02-11T04:12:00.000Z",
      finishedAt: "2026-02-11T04:12:00.000Z"
    },
    version: 17
  },
  {
    id: "run_lima-012",
    name: "Lima Rollout Canary",
    status: "running",
    priority: "high",
    source: "manual",
    ownerId: "usr_release-0001",
    assigneeId: "usr_release-0002",
    widgetIds: ["wid_chart-003", "wid_stat-007", "wid_feed-002"],
    health: "degraded",
    progress: { currentStep: 6, totalSteps: 11, percent: 54.5, etaSeconds: 900 },
    tags: ["release", "canary"],
    timestamps: {
      ...BASE_TIMESTAMPS,
      createdAt: "2026-02-16T04:00:00.000Z",
      startedAt: "2026-02-16T04:05:00.000Z",
      updatedAt: "2026-02-16T04:29:00.000Z"
    },
    version: 6
  }
];

export function getRunFixtureById(id: string): RunSummary | undefined {
  return RUN_FIXTURES.find((run) => run.id === id);
}

export function getRunFixtures(): readonly RunSummary[] {
  return RUN_FIXTURES;
}

export function parseRunFixtures(): readonly RunSummary[] {
  return RUN_FIXTURES.map((run) =>
    parseOrThrow(RunSummarySchema, run, { resource: "run", operation: "fixture-parse" })
  );
}
