import {
  DEFAULT_DETERMINISTIC_EXECUTION_POLICY,
  FactoryExecutionEnvelope,
  FactoryExecutionRequest,
  FeatureFlags,
  WorkerExecutionContext,
  WorkerId,
  assertFactoryExecutionRequest,
  createFeatureFlags,
} from "../contracts/FactoryContracts";
import {
  AgentExecutionResult,
  assertAgentExecutionResult,
} from "../contracts/AgentInterface";
import {
  JsonObject,
  JsonValue,
  canonicalizeJsonValue,
  stringifyCanonicalJson,
} from "../shared/DeterministicJson";
import {
  DeepReadonly,
  cloneAndFreezeJsonObject,
  cloneAndFreezeJsonValue,
  deepFreeze,
} from "../shared/Immutability";
import { HashProvider, hashText } from "../shared/Hashing";

export interface ContextGuardOptions {
  readonly maxPayloadBytes?: number;
  readonly forbidTemporalPayloadKeys?: boolean;
}

const TEMPORAL_KEY_PATTERN = /(?:^|_)(?:date|time|timestamp|clock|epoch)(?:$|_)/i;

function estimateUtf8ByteLength(text: string): number {
  return Buffer.from(text, "utf8").byteLength;
}

function deepMergeState(
  current: Readonly<Record<string, JsonValue>>,
  next: Readonly<Record<string, JsonValue>>,
): Readonly<Record<string, JsonValue>> {
  const output: Record<string, JsonValue> = {};
  const allKeys = new Set<string>([...Object.keys(current), ...Object.keys(next)]);
  for (const key of Array.from(allKeys).sort((left, right) => left.localeCompare(right))) {
    if (key in next) {
      const nextValue = next[key];
      if (nextValue === undefined) {
        throw new Error(`State key ${key} unexpectedly resolved as undefined.`);
      }
      output[key] = canonicalizeJsonValue(nextValue);
      continue;
    }
    const currentValue = current[key];
    if (currentValue === undefined) {
      throw new Error(`State key ${key} unexpectedly resolved as undefined.`);
    }
    output[key] = canonicalizeJsonValue(currentValue);
  }
  return deepFreeze(output);
}

function assertNoTemporalKeys(value: JsonValue, pathLabel: string): void {
  if (Array.isArray(value)) {
    for (const [index, child] of value.entries()) {
      assertNoTemporalKeys(child, `${pathLabel}[${index}]`);
    }
    return;
  }

  if (value !== null && typeof value === "object") {
    const objectValue = value as JsonObject;
    for (const key of Object.keys(objectValue)) {
      if (TEMPORAL_KEY_PATTERN.test(key)) {
        throw new Error(`Temporal payload key is forbidden: ${pathLabel}.${key}`);
      }
      const child = objectValue[key];
      if (child === undefined) {
        throw new Error(`Temporal key scan encountered undefined at ${pathLabel}.${key}`);
      }
      assertNoTemporalKeys(child, `${pathLabel}.${key}`);
    }
  }
}

export class ContextGuard {
  private readonly maxPayloadBytes: number;
  private readonly forbidTemporalPayloadKeys: boolean;
  private readonly hasher: HashProvider;

  constructor(hasher: HashProvider, options: ContextGuardOptions = {}) {
    this.maxPayloadBytes = options.maxPayloadBytes ?? 512_000;
    this.forbidTemporalPayloadKeys = options.forbidTemporalPayloadKeys ?? true;
    this.hasher = hasher;
  }

  createEnvelope(request: FactoryExecutionRequest): FactoryExecutionEnvelope {
    assertFactoryExecutionRequest(request, "request");
    const normalizedPayload = cloneAndFreezeJsonObject(request.payload);
    const serialized = stringifyCanonicalJson(normalizedPayload);
    const payloadBytes = estimateUtf8ByteLength(serialized);
    if (payloadBytes > this.maxPayloadBytes) {
      throw new Error(
        `Payload size ${payloadBytes} exceeds max deterministic limit ${this.maxPayloadBytes}.`,
      );
    }
    if (this.forbidTemporalPayloadKeys) {
      assertNoTemporalKeys(normalizedPayload, "request.payload");
    }

    const featureFlags: FeatureFlags = createFeatureFlags(request.featureFlags);
    const payloadHash = hashText(serialized, this.hasher);

    const envelope: FactoryExecutionEnvelope = {
      request: {
        ...request,
        payload: normalizedPayload,
      },
      normalizedFeatureFlags: featureFlags,
      policy: DEFAULT_DETERMINISTIC_EXECUTION_POLICY,
      payloadHash,
    };
    return deepFreeze(envelope);
  }

  createWorkerContext(
    envelope: FactoryExecutionEnvelope,
    workerId: WorkerId,
    inheritedState: Readonly<Record<string, JsonValue>>,
  ): DeepReadonly<WorkerExecutionContext> {
    const immutableInherited = cloneAndFreezeJsonValue(inheritedState) as Readonly<
      Record<string, JsonValue>
    >;
    const immutablePayload = cloneAndFreezeJsonObject(envelope.request.payload);

    const context: WorkerExecutionContext = {
      runId: envelope.request.runId,
      workerId,
      executionSeed: envelope.request.executionSeed,
      featureFlags: envelope.normalizedFeatureFlags,
      payload: immutablePayload,
      inheritedState: immutableInherited,
    };
    return deepFreeze(context);
  }

  mergeState(
    currentState: Readonly<Record<string, JsonValue>>,
    result: AgentExecutionResult,
  ): Readonly<Record<string, JsonValue>> {
    assertAgentExecutionResult(result, "result");
    return deepMergeState(currentState, result.output);
  }

  validateAgentResult(result: AgentExecutionResult, workerId: WorkerId): AgentExecutionResult {
    assertAgentExecutionResult(result, "result");
    if (result.workerId !== workerId) {
      throw new Error(
        `Agent result workerId mismatch. Expected ${workerId}, received ${result.workerId}.`,
      );
    }
    if (this.forbidTemporalPayloadKeys) {
      assertNoTemporalKeys(result.output, `${workerId}.output`);
      assertNoTemporalKeys(result.metadata, `${workerId}.metadata`);
    }

    return deepFreeze({
      ...result,
      output: cloneAndFreezeJsonObject(result.output),
      metadata: cloneAndFreezeJsonObject(result.metadata),
      fileChanges: deepFreeze([...result.fileChanges]),
      checks: deepFreeze([...result.checks]),
    });
  }
}
