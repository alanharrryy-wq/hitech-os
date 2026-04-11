import { AgentExecutionResult, assertAgentExecutionResult } from "./AgentInterface";
import { BundleFileChange, BundleStatus, summarizeBundleChanges } from "./BundleSchema";
import {
  FeatureFlags,
  WorkerId,
  assertRunId,
  normalizeRequestedWorkers,
} from "./FactoryContracts";
import { JsonObject, JsonValue, assertJsonObject } from "../shared/DeterministicJson";
import { HashProvider, hashJsonValue } from "../shared/Hashing";
import { normalizeRepoPath } from "../shared/Pathing";

export interface AgentExecutionRecord {
  readonly workerId: WorkerId;
  readonly orderIndex: number;
  readonly status: AgentExecutionResult["status"];
  readonly summary: string;
  readonly outputHash: string;
  readonly changedPaths: readonly string[];
}

export interface DeterministicExecutionReport {
  readonly runId: string;
  readonly baseRef: string;
  readonly executionSeed: string;
  readonly requestedWorkers: readonly WorkerId[];
  readonly featureFlags: FeatureFlags;
  readonly aggregateStatus: BundleStatus;
  readonly records: readonly AgentExecutionRecord[];
  readonly summary: JsonObject;
}

function validateRecord(record: AgentExecutionRecord, contextLabel: string): void {
  if (!Number.isInteger(record.orderIndex) || record.orderIndex < 0) {
    throw new Error(`${contextLabel}.orderIndex must be an integer >= 0.`);
  }
  if (record.summary.trim().length === 0) {
    throw new Error(`${contextLabel}.summary must not be empty.`);
  }
  if (record.outputHash.length !== 64) {
    throw new Error(`${contextLabel}.outputHash must be sha256.`);
  }
}

function deriveAggregateStatus(records: readonly AgentExecutionResult[]): BundleStatus {
  if (records.some((record) => record.status === "FAIL")) {
    return "FAIL";
  }
  if (records.some((record) => record.status === "BLOCKED")) {
    return "BLOCKED";
  }
  if (records.some((record) => record.status === "WARN")) {
    return "WARN";
  }
  return "PASS";
}

export function createExecutionReport(
  runId: string,
  baseRef: string,
  executionSeed: string,
  requestedWorkers: readonly WorkerId[],
  featureFlags: FeatureFlags,
  results: readonly AgentExecutionResult[],
  hasher: HashProvider,
): DeterministicExecutionReport {
  assertRunId(runId, "runId");
  if (baseRef.trim().length === 0) {
    throw new Error("baseRef must not be empty.");
  }
  if (executionSeed.trim().length === 0) {
    throw new Error("executionSeed must not be empty.");
  }

  const normalizedWorkers = normalizeRequestedWorkers(requestedWorkers);
  const records: AgentExecutionRecord[] = [];
  const allChanges: BundleFileChange[] = [];

  for (const [index, result] of results.entries()) {
    assertAgentExecutionResult(result, `results[${index}]`);
    const outputHash = hashJsonValue(result.output, hasher);
    const changedPaths = result.fileChanges
      .map((change) => normalizeRepoPath(change.path))
      .sort((left, right) => left.localeCompare(right));

    records.push({
      workerId: result.workerId,
      orderIndex: index,
      status: result.status,
      summary: result.summary,
      outputHash,
      changedPaths,
    });

    allChanges.push(...result.fileChanges);
  }

  const aggregateStatus = deriveAggregateStatus(results);
  const changeSummary = summarizeBundleChanges(allChanges);
  const summary: JsonObject = {
    workerCount: records.length,
    changeSummary,
    status: aggregateStatus,
  };

  const report: DeterministicExecutionReport = {
    runId,
    baseRef,
    executionSeed,
    requestedWorkers: normalizedWorkers,
    featureFlags,
    aggregateStatus,
    records,
    summary,
  };

  assertExecutionReport(report, "executionReport");
  return report;
}

export function assertExecutionReport(
  report: DeterministicExecutionReport,
  contextLabel: string,
): void {
  assertRunId(report.runId, `${contextLabel}.runId`);
  if (report.baseRef.trim().length === 0) {
    throw new Error(`${contextLabel}.baseRef must not be empty.`);
  }
  if (report.executionSeed.trim().length === 0) {
    throw new Error(`${contextLabel}.executionSeed must not be empty.`);
  }
  assertJsonObject(report.summary, `${contextLabel}.summary`);

  for (const [index, record] of report.records.entries()) {
    validateRecord(record, `${contextLabel}.records[${index}]`);
  }
}

export function executionReportToJson(report: DeterministicExecutionReport): JsonValue {
  assertExecutionReport(report, "executionReportToJson");
  return {
    runId: report.runId,
    baseRef: report.baseRef,
    executionSeed: report.executionSeed,
    requestedWorkers: report.requestedWorkers,
    featureFlags: report.featureFlags,
    aggregateStatus: report.aggregateStatus,
    records: report.records.map((record) => ({
      workerId: record.workerId,
      orderIndex: record.orderIndex,
      status: record.status,
      summary: record.summary,
      outputHash: record.outputHash,
      changedPaths: record.changedPaths,
    })),
    summary: report.summary,
  };
}

export function hashExecutionReport(
  report: DeterministicExecutionReport,
  hasher: HashProvider,
): string {
  return hashJsonValue(executionReportToJson(report), hasher);
}
