import { JsonObject, JsonValue, assertJsonObject } from "../shared/DeterministicJson";
import { deepReadonlyRecord } from "../shared/Immutability";

export const FACTORY_BLOCK_SEQUENCE = [
  "A_core",
  "B_tooling",
  "C_features",
  "D_validation",
  "Z_aggregator",
] as const;

export type FactoryBlockId = (typeof FACTORY_BLOCK_SEQUENCE)[number];

export type WorkerId = string;

export const WORKER_ID_PATTERN = /^[A-Z]_[a-z0-9]+(?:_[a-z0-9]+)*$/;
export const RUN_ID_PATTERN = /^[a-z][a-z0-9]*_[0-9]{8}_[0-9]{6}_[a-f0-9]{8}_[0-9]{3}$/;

export const FEATURE_FLAG_KEYS = [
  "allowExperimentalWorkers",
  "allowCrossModuleImports",
  "allowTemporalSignals",
  "allowNonDeterministicApis",
] as const;

export type FeatureFlagKey = (typeof FEATURE_FLAG_KEYS)[number];
export type FeatureFlags = Readonly<Record<FeatureFlagKey, boolean>>;

export interface DeterministicExecutionPolicy {
  readonly enforceFeatureFlagsOffByDefault: boolean;
  readonly forbidTemporalDependencies: boolean;
  readonly forbidCrossWorkerStateMutation: boolean;
  readonly deterministicWorkerOrder: "fixed" | "lexicographic";
}

export const DEFAULT_DETERMINISTIC_EXECUTION_POLICY: DeterministicExecutionPolicy = {
  enforceFeatureFlagsOffByDefault: true,
  forbidTemporalDependencies: true,
  forbidCrossWorkerStateMutation: true,
  deterministicWorkerOrder: "fixed",
};

export interface FactoryExecutionRequest {
  readonly runId: string;
  readonly baseRef: string;
  readonly executionSeed: string;
  readonly payload: JsonObject;
  readonly featureFlags?: Readonly<Partial<Record<FeatureFlagKey, boolean>>>;
  readonly requestedWorkers?: readonly WorkerId[];
}

export interface FactoryExecutionEnvelope {
  readonly request: FactoryExecutionRequest;
  readonly normalizedFeatureFlags: FeatureFlags;
  readonly policy: DeterministicExecutionPolicy;
  readonly payloadHash: string;
}

export interface WorkerExecutionContext {
  readonly runId: string;
  readonly workerId: WorkerId;
  readonly executionSeed: string;
  readonly featureFlags: FeatureFlags;
  readonly payload: JsonObject;
  readonly inheritedState: Readonly<Record<string, JsonValue>>;
}

export function assertWorkerId(value: string, contextLabel: string): asserts value is WorkerId {
  if (!WORKER_ID_PATTERN.test(value)) {
    throw new Error(`${contextLabel} must match ${WORKER_ID_PATTERN.source}.`);
  }
}

export function assertRunId(value: string, contextLabel: string): void {
  if (!RUN_ID_PATTERN.test(value)) {
    throw new Error(`${contextLabel} must match ${RUN_ID_PATTERN.source}.`);
  }
}

export function assertFactoryExecutionRequest(
  request: FactoryExecutionRequest,
  contextLabel: string,
): void {
  assertRunId(request.runId, `${contextLabel}.runId`);
  if (request.baseRef.trim().length === 0) {
    throw new Error(`${contextLabel}.baseRef must not be empty.`);
  }
  if (request.executionSeed.trim().length === 0) {
    throw new Error(`${contextLabel}.executionSeed must not be empty.`);
  }
  assertJsonObject(request.payload, `${contextLabel}.payload`);

  if (request.requestedWorkers !== undefined) {
    for (const worker of request.requestedWorkers) {
      assertWorkerId(worker, `${contextLabel}.requestedWorkers`);
    }
  }
}

export function createFeatureFlags(
  overrides: Readonly<Partial<Record<FeatureFlagKey, boolean>>> = {},
): FeatureFlags {
  const output: Record<FeatureFlagKey, boolean> = {
    allowExperimentalWorkers: false,
    allowCrossModuleImports: false,
    allowTemporalSignals: false,
    allowNonDeterministicApis: false,
  };

  for (const key of FEATURE_FLAG_KEYS) {
    const override = overrides[key];
    if (override !== undefined) {
      output[key] = override;
    }
  }

  return deepReadonlyRecord(output);
}

export function normalizeRequestedWorkers(
  requestedWorkers: readonly WorkerId[] | undefined,
): readonly WorkerId[] {
  if (requestedWorkers === undefined || requestedWorkers.length === 0) {
    return FACTORY_BLOCK_SEQUENCE;
  }

  const uniqueWorkers = Array.from(new Set(requestedWorkers));
  for (const worker of uniqueWorkers) {
    assertWorkerId(worker, "requestedWorkers");
  }
  return uniqueWorkers.sort((left, right) => left.localeCompare(right));
}
