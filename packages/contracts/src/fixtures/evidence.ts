import { EvidenceRef, EvidenceRefSchema } from "../mission-control/evidence.js";
import { parseOrThrow } from "../parsing.js";

export const EVIDENCE_FIXTURES: readonly EvidenceRef[] = [
  {
    id: "evi_alpha-001",
    runId: "run_alpha-001",
    kind: "log",
    label: "runtime.log",
    mime: "text/plain",
    sizeBytes: 16_238,
    createdAt: "2026-02-15T08:10:00.000Z",
    createdBy: "usr_ops-0002",
    location: {
      storage: "local",
      path: "C:/evidence/run_alpha-001/runtime.log",
      bucket: null,
      region: null
    },
    checksum: {
      algorithm: "sha256",
      value: "1111111111111111111111111111111111111111111111111111111111111111"
    },
    redacted: false,
    tags: ["runtime", "log"]
  },
  {
    id: "evi_alpha-002",
    runId: "run_alpha-001",
    kind: "artifact",
    label: "bundle.tar",
    mime: "application/x-tar",
    sizeBytes: 523_000,
    createdAt: "2026-02-15T08:11:00.000Z",
    createdBy: "usr_ops-0002",
    location: {
      storage: "s3",
      path: "alpha/bundle.tar",
      bucket: "hitech-evidence",
      region: "us-east-1"
    },
    checksum: {
      algorithm: "sha512",
      value:
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    redacted: false,
    tags: ["artifact", "release"]
  },
  {
    id: "evi_charlie-001",
    runId: "run_charlie-003",
    kind: "trace",
    label: "security.trace",
    mime: "application/json",
    sizeBytes: 88_201,
    createdAt: "2026-02-15T05:05:00.000Z",
    createdBy: "usr_sec-0001",
    location: {
      storage: "local",
      path: "C:/evidence/run_charlie-003/security.trace.json",
      bucket: null,
      region: null
    },
    checksum: {
      algorithm: "sha256",
      value: "2222222222222222222222222222222222222222222222222222222222222222"
    },
    redacted: true,
    tags: ["trace", "security"]
  },
  {
    id: "evi_delta-001",
    runId: "run_delta-004",
    kind: "report",
    label: "reconcile-report.md",
    mime: "text/markdown",
    sizeBytes: 12_118,
    createdAt: "2026-02-13T18:45:00.000Z",
    createdBy: "usr_data-0002",
    location: {
      storage: "gcs",
      path: "delta/reconcile-report.md",
      bucket: "hitech-reports",
      region: "us-central1"
    },
    checksum: {
      algorithm: "sha256",
      value: "3333333333333333333333333333333333333333333333333333333333333333"
    },
    redacted: false,
    tags: ["report", "finance"]
  },
  {
    id: "evi_echo-001",
    runId: "run_echo-005",
    kind: "screenshot",
    label: "contract-failure.png",
    mime: "image/png",
    sizeBytes: 62_322,
    createdAt: "2026-02-12T03:19:00.000Z",
    createdBy: "usr_api-0003",
    location: {
      storage: "local",
      path: "C:/evidence/run_echo-005/contract-failure.png",
      bucket: null,
      region: null
    },
    checksum: {
      algorithm: "md5",
      value: "44444444444444444444444444444444"
    },
    redacted: false,
    tags: ["ui", "failure"]
  },
  {
    id: "evi_kilo-001",
    runId: "run_kilo-011",
    kind: "metric-snapshot",
    label: "queue-pressure.json",
    mime: "application/json",
    sizeBytes: 4_298,
    createdAt: "2026-02-11T04:11:00.000Z",
    createdBy: "usr_queue-0003",
    location: {
      storage: "azure",
      path: "kilo/queue-pressure.json",
      bucket: "ops-artifacts",
      region: "eastus"
    },
    checksum: {
      algorithm: "sha256",
      value: "5555555555555555555555555555555555555555555555555555555555555555"
    },
    redacted: false,
    tags: ["queue", "metrics"]
  },
  {
    id: "evi_lima-001",
    runId: "run_lima-012",
    kind: "log",
    label: "rollout.log",
    mime: "text/plain",
    sizeBytes: 22_189,
    createdAt: "2026-02-16T04:30:00.000Z",
    createdBy: "usr_release-0002",
    location: {
      storage: "local",
      path: "C:/evidence/run_lima-012/rollout.log",
      bucket: null,
      region: null
    },
    checksum: {
      algorithm: "sha256",
      value: "6666666666666666666666666666666666666666666666666666666666666666"
    },
    redacted: false,
    tags: ["release", "log"]
  }
];

export function getEvidenceFixturesByRunId(runId: string): readonly EvidenceRef[] {
  return EVIDENCE_FIXTURES.filter((item) => item.runId === runId);
}

export function parseEvidenceFixtures(): readonly EvidenceRef[] {
  return EVIDENCE_FIXTURES.map((item) =>
    parseOrThrow(EvidenceRefSchema, item, { resource: "evidence", operation: "fixture-parse" })
  );
}
