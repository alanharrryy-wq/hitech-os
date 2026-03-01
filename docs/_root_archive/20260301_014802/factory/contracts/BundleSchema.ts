import { WorkerId, assertWorkerId } from "./FactoryContracts";
import { JsonObject, JsonValue, assertJsonObject } from "../shared/DeterministicJson";
import {
  assertRepoRelativePath,
  compareRepoPaths,
  normalizeRepoPath,
} from "../shared/Pathing";

export type BundleStatus = "PENDING" | "PASS" | "BLOCKED" | "WARN" | "FAIL";

export type FileChangeKind = "added" | "modified" | "deleted" | "renamed";

export interface BundleFileChange {
  readonly workerId: WorkerId;
  readonly path: string;
  readonly kind: FileChangeKind;
  readonly sha256: string;
  readonly bytes: number;
  readonly summary: string;
}

export interface BundleCheckResult {
  readonly name: string;
  readonly required: boolean;
  readonly rc: number;
  readonly details: string;
}

export interface WorkerBundle {
  readonly workerId: WorkerId;
  readonly status: BundleStatus;
  readonly summary: string;
  readonly changes: readonly BundleFileChange[];
  readonly checks: readonly BundleCheckResult[];
  readonly logs: readonly string[];
  readonly metadata: JsonObject;
}

export interface IntegratorBundle {
  readonly workerId: "Z_aggregator";
  readonly status: BundleStatus;
  readonly summary: string;
  readonly changes: readonly BundleFileChange[];
  readonly checks: readonly BundleCheckResult[];
  readonly logs: readonly string[];
  readonly finalReportPath: string;
  readonly metadata: JsonObject;
}

export const REQUIRED_WORKER_ARTIFACTS = [
  "STATUS.json",
  "SUMMARY.md",
  "FILES_CHANGED.json",
  "DIFF.patch",
  "SUGGESTIONS.md",
  "SCOPE_LOCK.json",
  "HANDOFF_NOTE.json",
  "LOGS/INDEX.json",
] as const;

export const REQUIRED_AGGREGATOR_ARTIFACTS = [
  "STATUS.json",
  "FINAL_REPORT.txt",
  "FILES_CHANGED.json",
  "DIFF.patch",
  "MERGE_PLAN.md",
  "LOGS/INDEX.json",
] as const;

const SHA256_PATTERN = /^[a-f0-9]{64}$/;

export function assertBundleStatus(status: string, contextLabel: string): asserts status is BundleStatus {
  const allowed: readonly BundleStatus[] = ["PENDING", "PASS", "BLOCKED", "WARN", "FAIL"];
  if (!allowed.includes(status as BundleStatus)) {
    throw new Error(`${contextLabel} is invalid. Received: ${status}`);
  }
}

export function assertBundleFileChange(
  change: BundleFileChange,
  contextLabel: string,
): void {
  assertWorkerId(change.workerId, `${contextLabel}.workerId`);
  assertRepoRelativePath(change.path, `${contextLabel}.path`);

  const validKinds: readonly FileChangeKind[] = ["added", "modified", "deleted", "renamed"];
  if (!validKinds.includes(change.kind)) {
    throw new Error(`${contextLabel}.kind is invalid.`);
  }
  if (!SHA256_PATTERN.test(change.sha256)) {
    throw new Error(`${contextLabel}.sha256 must be a 64-char lowercase hex string.`);
  }
  if (!Number.isInteger(change.bytes) || change.bytes < 0) {
    throw new Error(`${contextLabel}.bytes must be an integer >= 0.`);
  }
  if (change.summary.trim().length === 0) {
    throw new Error(`${contextLabel}.summary must not be empty.`);
  }
}

function assertBundleCheckResult(check: BundleCheckResult, contextLabel: string): void {
  if (check.name.trim().length === 0) {
    throw new Error(`${contextLabel}.name must not be empty.`);
  }
  if (!Number.isInteger(check.rc)) {
    throw new Error(`${contextLabel}.rc must be an integer.`);
  }
  if (check.required !== true && check.required !== false) {
    throw new Error(`${contextLabel}.required must be boolean.`);
  }
}

function assertLogPath(logPath: string, contextLabel: string): void {
  const normalized = assertRepoRelativePath(logPath, contextLabel);
  if (!normalized.includes("/LOGS/") && !normalized.endsWith("LOGS/INDEX.json")) {
    throw new Error(`${contextLabel} must point to LOGS entries.`);
  }
}

function assertMetadata(metadata: JsonObject, contextLabel: string): void {
  assertJsonObject(metadata, contextLabel);
}

export function assertWorkerBundle(bundle: WorkerBundle, contextLabel: string): void {
  assertWorkerId(bundle.workerId, `${contextLabel}.workerId`);
  assertBundleStatus(bundle.status, `${contextLabel}.status`);
  if (bundle.summary.trim().length === 0) {
    throw new Error(`${contextLabel}.summary must not be empty.`);
  }
  if (bundle.changes.length === 0) {
    throw new Error(`${contextLabel}.changes must not be empty.`);
  }
  for (const [index, change] of bundle.changes.entries()) {
    assertBundleFileChange(change, `${contextLabel}.changes[${index}]`);
  }
  for (const [index, check] of bundle.checks.entries()) {
    assertBundleCheckResult(check, `${contextLabel}.checks[${index}]`);
  }
  for (const [index, logPath] of bundle.logs.entries()) {
    assertLogPath(logPath, `${contextLabel}.logs[${index}]`);
  }
  assertMetadata(bundle.metadata, `${contextLabel}.metadata`);
}

export function assertIntegratorBundle(bundle: IntegratorBundle, contextLabel: string): void {
  if (bundle.workerId !== "Z_aggregator") {
    throw new Error(`${contextLabel}.workerId must be Z_aggregator.`);
  }
  assertBundleStatus(bundle.status, `${contextLabel}.status`);
  if (bundle.summary.trim().length === 0) {
    throw new Error(`${contextLabel}.summary must not be empty.`);
  }
  assertRepoRelativePath(bundle.finalReportPath, `${contextLabel}.finalReportPath`);
  for (const [index, change] of bundle.changes.entries()) {
    assertBundleFileChange(change, `${contextLabel}.changes[${index}]`);
  }
  for (const [index, check] of bundle.checks.entries()) {
    assertBundleCheckResult(check, `${contextLabel}.checks[${index}]`);
  }
  for (const [index, logPath] of bundle.logs.entries()) {
    assertLogPath(logPath, `${contextLabel}.logs[${index}]`);
  }
  assertMetadata(bundle.metadata, `${contextLabel}.metadata`);
}

function bundleChangeComparator(left: BundleFileChange, right: BundleFileChange): number {
  const byPath = compareRepoPaths(left.path, right.path);
  if (byPath !== 0) {
    return byPath;
  }
  const byKind = left.kind.localeCompare(right.kind);
  if (byKind !== 0) {
    return byKind;
  }
  return left.workerId.localeCompare(right.workerId);
}

export function normalizeBundleChanges(
  changes: readonly BundleFileChange[],
): readonly BundleFileChange[] {
  const normalized = changes.map((change) => ({
    ...change,
    path: normalizeRepoPath(change.path),
  }));
  return normalized.sort(bundleChangeComparator);
}

export function summarizeBundleChanges(changes: readonly BundleFileChange[]): JsonObject {
  let added = 0;
  let modified = 0;
  let deleted = 0;
  let renamed = 0;
  let totalBytes = 0;

  for (const change of changes) {
    totalBytes += change.bytes;
    switch (change.kind) {
      case "added":
        added += 1;
        break;
      case "modified":
        modified += 1;
        break;
      case "deleted":
        deleted += 1;
        break;
      case "renamed":
        renamed += 1;
        break;
      default: {
        const impossible: never = change.kind;
        throw new Error(`Unsupported change kind: ${impossible}`);
      }
    }
  }

  return {
    added,
    modified,
    deleted,
    renamed,
    totalBytes,
    totalFiles: changes.length,
  };
}

export function bundleChecksToJson(checks: readonly BundleCheckResult[]): JsonValue {
  return checks.map((check) => ({
    name: check.name,
    required: check.required,
    rc: check.rc,
    details: check.details,
  }));
}
