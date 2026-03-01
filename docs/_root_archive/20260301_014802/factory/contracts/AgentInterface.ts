import { BundleCheckResult, BundleFileChange } from "./BundleSchema";
import { WorkerExecutionContext, WorkerId, assertWorkerId } from "./FactoryContracts";
import { JsonObject, JsonValue, assertJsonObject } from "../shared/DeterministicJson";
import { assertRepoRelativePath } from "../shared/Pathing";

export interface AgentIsolationBoundary {
  readonly allowedReadRoots: readonly string[];
  readonly allowedWriteRoots: readonly string[];
  readonly deniesCrossWorkerBundles: boolean;
}

export interface AgentCapabilities {
  readonly supportsDryRun: boolean;
  readonly supportsSnapshotOutput: boolean;
  readonly emitsDiffs: boolean;
}

export interface AgentExecutionResult {
  readonly workerId: WorkerId;
  readonly status: "PASS" | "BLOCKED" | "FAIL" | "WARN";
  readonly summary: string;
  readonly fileChanges: readonly BundleFileChange[];
  readonly checks: readonly BundleCheckResult[];
  readonly metadata: JsonObject;
  readonly output: JsonObject;
}

export interface FactoryAgent {
  readonly workerId: WorkerId;
  readonly description: string;
  readonly deterministicOrderHint: number;
  readonly boundaries: AgentIsolationBoundary;
  readonly capabilities: AgentCapabilities;
  execute(context: WorkerExecutionContext): Promise<AgentExecutionResult>;
}

export interface AgentRegistrationRecord {
  readonly workerId: WorkerId;
  readonly deterministicOrderHint: number;
  readonly description: string;
}

const VALID_AGENT_STATUS: readonly AgentExecutionResult["status"][] = [
  "PASS",
  "BLOCKED",
  "FAIL",
  "WARN",
];

function assertBoundaryPathList(paths: readonly string[], contextLabel: string): void {
  if (paths.length === 0) {
    throw new Error(`${contextLabel} must not be empty.`);
  }

  for (const [index, pathValue] of paths.entries()) {
    assertRepoRelativePath(pathValue, `${contextLabel}[${index}]`);
  }
}

export function assertAgentIsolationBoundary(
  boundaries: AgentIsolationBoundary,
  contextLabel: string,
): void {
  assertBoundaryPathList(boundaries.allowedReadRoots, `${contextLabel}.allowedReadRoots`);
  assertBoundaryPathList(boundaries.allowedWriteRoots, `${contextLabel}.allowedWriteRoots`);
  if (boundaries.deniesCrossWorkerBundles !== true && boundaries.deniesCrossWorkerBundles !== false) {
    throw new Error(`${contextLabel}.deniesCrossWorkerBundles must be boolean.`);
  }
}

export function assertFactoryAgent(agent: FactoryAgent, contextLabel: string): void {
  assertWorkerId(agent.workerId, `${contextLabel}.workerId`);
  if (agent.description.trim().length === 0) {
    throw new Error(`${contextLabel}.description must not be empty.`);
  }
  if (!Number.isInteger(agent.deterministicOrderHint) || agent.deterministicOrderHint < 0) {
    throw new Error(`${contextLabel}.deterministicOrderHint must be an integer >= 0.`);
  }
  assertAgentIsolationBoundary(agent.boundaries, `${contextLabel}.boundaries`);

  const capabilityValues: readonly JsonValue[] = [
    agent.capabilities.supportsDryRun,
    agent.capabilities.supportsSnapshotOutput,
    agent.capabilities.emitsDiffs,
  ];
  for (const value of capabilityValues) {
    if (typeof value !== "boolean") {
      throw new Error(`${contextLabel}.capabilities must only contain booleans.`);
    }
  }
}

export function assertAgentExecutionResult(
  result: AgentExecutionResult,
  contextLabel: string,
): void {
  assertWorkerId(result.workerId, `${contextLabel}.workerId`);
  if (!VALID_AGENT_STATUS.includes(result.status)) {
    throw new Error(`${contextLabel}.status is invalid.`);
  }
  if (result.summary.trim().length === 0) {
    throw new Error(`${contextLabel}.summary must not be empty.`);
  }
  if (result.fileChanges.length === 0) {
    throw new Error(`${contextLabel}.fileChanges must not be empty.`);
  }
  assertJsonObject(result.metadata, `${contextLabel}.metadata`);
  assertJsonObject(result.output, `${contextLabel}.output`);
}
