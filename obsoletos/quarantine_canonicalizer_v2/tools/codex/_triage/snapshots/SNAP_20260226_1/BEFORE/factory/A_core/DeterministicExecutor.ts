import { FactoryAgent } from "../contracts/AgentInterface";
import { FactoryExecutionEnvelope, WorkerId } from "../contracts/FactoryContracts";
import { AgentExecutionResult } from "../contracts/AgentInterface";
import { JsonValue } from "../shared/DeterministicJson";
import { HashProvider, hashJsonValue } from "../shared/Hashing";
import { ContextGuard } from "./ContextGuard";

export interface ExecutionTraceRecord {
  readonly workerId: WorkerId;
  readonly position: number;
  readonly contextHash: string;
  readonly outputHash: string;
  readonly status: AgentExecutionResult["status"];
}

export interface DeterministicExecutionOutcome {
  readonly orderedWorkerIds: readonly WorkerId[];
  readonly results: readonly AgentExecutionResult[];
  readonly trace: readonly ExecutionTraceRecord[];
}

export interface DeterministicExecutorOptions {
  readonly failFastOnError?: boolean;
}

function compareAgents(left: FactoryAgent, right: FactoryAgent): number {
  if (left.deterministicOrderHint !== right.deterministicOrderHint) {
    return left.deterministicOrderHint - right.deterministicOrderHint;
  }
  return left.workerId.localeCompare(right.workerId);
}

export class DeterministicExecutor {
  private readonly contextGuard: ContextGuard;
  private readonly hasher: HashProvider;
  private readonly failFastOnError: boolean;

  constructor(
    contextGuard: ContextGuard,
    hasher: HashProvider,
    options: DeterministicExecutorOptions = {},
  ) {
    this.contextGuard = contextGuard;
    this.hasher = hasher;
    this.failFastOnError = options.failFastOnError ?? true;
  }

  async execute(
    envelope: FactoryExecutionEnvelope,
    agents: readonly FactoryAgent[],
  ): Promise<DeterministicExecutionOutcome> {
    const orderedAgents = [...agents].sort(compareAgents);
    const orderedWorkerIds = orderedAgents.map((agent) => agent.workerId);

    const results: AgentExecutionResult[] = [];
    const trace: ExecutionTraceRecord[] = [];
    let inheritedState: Readonly<Record<string, JsonValue>> = {};

    for (const [position, agent] of orderedAgents.entries()) {
      const context = this.contextGuard.createWorkerContext(
        envelope,
        agent.workerId,
        inheritedState,
      );

      const contextHash = hashJsonValue(
        {
          runId: context.runId,
          workerId: context.workerId,
          featureFlags: context.featureFlags,
          payload: context.payload,
          inheritedState: context.inheritedState,
        },
        this.hasher,
      );

      const result = await agent.execute(context);
      const validated = this.contextGuard.validateAgentResult(result, agent.workerId);
      const outputHash = hashJsonValue(validated.output, this.hasher);

      results.push(validated);
      trace.push({
        workerId: agent.workerId,
        position,
        contextHash,
        outputHash,
        status: validated.status,
      });

      inheritedState = this.contextGuard.mergeState(inheritedState, validated);

      if (this.failFastOnError && (validated.status === "BLOCKED" || validated.status === "FAIL")) {
        break;
      }
    }

    return {
      orderedWorkerIds,
      results,
      trace,
    };
  }
}
