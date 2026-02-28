import { ActivityEvent, ActivityEventSchema } from "../mission-control/activity.js";
import { parseOrThrow } from "../parsing.js";

export const ACTIVITY_FIXTURES: readonly ActivityEvent[] = [
  {
    id: "act_20260215-run-alpha-created",
    type: "run.created",
    severity: "info",
    title: "Run Created",
    message: "Alpha Build Validation was created by operations.",
    actor: {
      type: "user",
      id: "usr_ops-0001",
      userId: "usr_ops-0001",
      displayName: "Ops Lead",
      avatarUrl: null
    },
    runId: "run_alpha-001",
    createdAt: "2026-02-15T08:00:00.000Z",
    acknowledged: true,
    metadata: {
      source: "manual",
      priority: "high"
    }
  },
  {
    id: "act_20260215-run-alpha-started",
    type: "run.started",
    severity: "info",
    title: "Run Started",
    message: "Worker fleet accepted Alpha Build Validation.",
    actor: {
      type: "service",
      id: "svc_scheduler",
      userId: null,
      displayName: "Scheduler Service",
      avatarUrl: null
    },
    runId: "run_alpha-001",
    createdAt: "2026-02-15T08:07:00.000Z",
    acknowledged: false,
    metadata: {
      workerPool: "compute-east-01",
      queueDepth: 2
    }
  },
  {
    id: "act_20260215-run-alpha-progress",
    type: "run.progress",
    severity: "debug",
    title: "Run Progress",
    message: "Alpha Build Validation reached step 4 of 10.",
    actor: {
      type: "service",
      id: "svc_pipeline",
      userId: null,
      displayName: "Pipeline Service",
      avatarUrl: null
    },
    runId: "run_alpha-001",
    createdAt: "2026-02-15T08:12:00.000Z",
    acknowledged: false,
    metadata: {
      currentStep: 4,
      totalSteps: 10,
      percent: 40
    }
  },
  {
    id: "act_20260214-charlie-paused",
    type: "run.paused",
    severity: "warn",
    title: "Run Paused",
    message: "Charlie Security Hardening paused due to elevated CPU usage.",
    actor: {
      type: "system",
      id: "sys_guardrail",
      userId: null,
      displayName: "System Guardrail",
      avatarUrl: null
    },
    runId: "run_charlie-003",
    createdAt: "2026-02-15T05:15:00.000Z",
    acknowledged: true,
    metadata: {
      threshold: 95,
      observed: 98
    }
  },
  {
    id: "act_20260212-echo-failed",
    type: "run.failed",
    severity: "error",
    title: "Run Failed",
    message: "Echo API Contract Checks failed because payload mismatch was detected.",
    actor: {
      type: "service",
      id: "svc_contract-checker",
      userId: null,
      displayName: "Contract Checker",
      avatarUrl: null
    },
    runId: "run_echo-005",
    createdAt: "2026-02-12T03:20:00.000Z",
    acknowledged: false,
    metadata: {
      schema: "RunsQueryResponse",
      expectedVersion: "2.0.0"
    }
  },
  {
    id: "act_20260211-kilo-alert",
    type: "system.alert",
    severity: "critical",
    title: "Queue Saturation",
    message: "Message queue pressure exceeded critical threshold in Kilo run.",
    actor: {
      type: "system",
      id: "sys_observer",
      userId: null,
      displayName: "System Observer",
      avatarUrl: null
    },
    runId: "run_kilo-011",
    createdAt: "2026-02-11T04:10:00.000Z",
    acknowledged: false,
    metadata: {
      queue: "primary-events",
      pressure: 0.97,
      threshold: 0.9
    }
  },
  {
    id: "act_20260213-delta-completed",
    type: "run.completed",
    severity: "info",
    title: "Run Completed",
    message: "Delta Data Backfill completed successfully.",
    actor: {
      type: "service",
      id: "svc_etl",
      userId: null,
      displayName: "ETL Service",
      avatarUrl: null
    },
    runId: "run_delta-004",
    createdAt: "2026-02-13T18:44:00.000Z",
    acknowledged: true,
    metadata: {
      rowsProcessed: 1_250_000,
      retryCount: 0
    }
  },
  {
    id: "act_20260216-lima-started",
    type: "run.started",
    severity: "info",
    title: "Canary Started",
    message: "Lima Rollout Canary started in region us-east.",
    actor: {
      type: "user",
      id: "usr_release-0001",
      userId: "usr_release-0001",
      displayName: "Release Manager",
      avatarUrl: null
    },
    runId: "run_lima-012",
    createdAt: "2026-02-16T04:05:00.000Z",
    acknowledged: false,
    metadata: {
      region: "us-east",
      deployment: "canary-14"
    }
  },
  {
    id: "act_20260216-lima-progress",
    type: "run.progress",
    severity: "debug",
    title: "Canary Progress",
    message: "Lima Rollout Canary reached 54.5% completion.",
    actor: {
      type: "service",
      id: "svc_release",
      userId: null,
      displayName: "Release Service",
      avatarUrl: null
    },
    runId: "run_lima-012",
    createdAt: "2026-02-16T04:29:00.000Z",
    acknowledged: false,
    metadata: {
      percent: 54.5,
      healthyNodes: 38,
      targetNodes: 70
    }
  },
  {
    id: "act_20260215-golf-scheduled",
    type: "run.queued",
    severity: "info",
    title: "Billing Run Scheduled",
    message: "Golf Billing Reconciliation is waiting for execution window.",
    actor: {
      type: "service",
      id: "svc_schedule",
      userId: null,
      displayName: "Scheduling Service",
      avatarUrl: null
    },
    runId: "run_golf-007",
    createdAt: "2026-02-15T18:05:00.000Z",
    acknowledged: true,
    metadata: {
      scheduledAt: "2026-02-16T06:00:00.000Z"
    }
  },
  {
    id: "act_20260210-hotel-canceled",
    type: "run.canceled",
    severity: "warn",
    title: "Run Canceled",
    message: "Hotel Cache Warmup canceled due to maintenance window overlap.",
    actor: {
      type: "user",
      id: "usr_platform-0002",
      userId: "usr_platform-0002",
      displayName: "Platform Engineer",
      avatarUrl: null
    },
    runId: "run_hotel-008",
    createdAt: "2026-02-10T11:12:00.000Z",
    acknowledged: true,
    metadata: {
      reason: "maintenance-window"
    }
  },
  {
    id: "act_20260216-india-widget",
    type: "widget.updated",
    severity: "info",
    title: "Widget Updated",
    message: "Feature matrix table columns were updated.",
    actor: {
      type: "user",
      id: "usr_pm-0001",
      userId: "usr_pm-0001",
      displayName: "Product Manager",
      avatarUrl: null
    },
    runId: "run_india-009",
    createdAt: "2026-02-16T01:20:00.000Z",
    acknowledged: false,
    metadata: {
      widgetId: "wid_table-006",
      columnCount: 8
    }
  },
  {
    id: "act_20260216-auth-login",
    type: "auth.login",
    severity: "info",
    title: "User Login",
    message: "Operations user authenticated for mission control.",
    actor: {
      type: "user",
      id: "usr_ops-0003",
      userId: "usr_ops-0003",
      displayName: "Ops Analyst",
      avatarUrl: null
    },
    runId: null,
    createdAt: "2026-02-16T05:12:00.000Z",
    acknowledged: true,
    metadata: {
      ip: "10.0.1.14",
      mfa: true
    }
  },
  {
    id: "act_20260216-auth-logout",
    type: "auth.logout",
    severity: "debug",
    title: "User Logout",
    message: "Operations user logged out.",
    actor: {
      type: "user",
      id: "usr_ops-0003",
      userId: "usr_ops-0003",
      displayName: "Ops Analyst",
      avatarUrl: null
    },
    runId: null,
    createdAt: "2026-02-16T05:42:00.000Z",
    acknowledged: true,
    metadata: {
      durationMinutes: 30
    }
  }
];

export function getActivityFixtures(): readonly ActivityEvent[] {
  return ACTIVITY_FIXTURES;
}

export function parseActivityFixtures(): readonly ActivityEvent[] {
  return ACTIVITY_FIXTURES.map((item) =>
    parseOrThrow(ActivityEventSchema, item, { resource: "activity", operation: "fixture-parse" })
  );
}
