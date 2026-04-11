import { FactoryAgent } from "../contracts/AgentInterface";
import {
  FactoryExecutionRequest,
  WorkerId,
  normalizeRequestedWorkers,
} from "../contracts/FactoryContracts";
import {
  DeterministicExecutionReport,
  createExecutionReport,
  hashExecutionReport,
} from "../contracts/ExecutionReport";
import { HashProvider } from "../shared/Hashing";
import { AgentRegistry } from "./AgentRegistry";
import {
  DeterministicExecutionOutcome,
  DeterministicExecutor,
} from "./DeterministicExecutor";
import { ContextGuard } from "./ContextGuard";

export interface CoreOrchestratorDependencies {
  readonly registry: AgentRegistry;
  readonly contextGuard: ContextGuard;
  readonly executor: DeterministicExecutor;
  readonly hasher: HashProvider;
}

export interface OrchestratorRunResult {
  readonly report: DeterministicExecutionReport;
  readonly reportHash: string;
  readonly results: DeterministicExecutionOutcome["results"];
  readonly trace: DeterministicExecutionOutcome["trace"];
}

export class CoreOrchestrator {
  private readonly registry: AgentRegistry;
  private readonly contextGuard: ContextGuard;
  private readonly executor: DeterministicExecutor;
  private readonly hasher: HashProvider;

  constructor(dependencies: CoreOrchestratorDependencies) {
    this.registry = dependencies.registry;
    this.contextGuard = dependencies.contextGuard;
    this.executor = dependencies.executor;
    this.hasher = dependencies.hasher;
  }

  registerAgent(agent: FactoryAgent): void {
    this.registry.register(agent);
  }

  listRegisteredWorkers(): readonly WorkerId[] {
    return this.registry.list().map((agent) => agent.workerId);
  }

  async execute(request: FactoryExecutionRequest): Promise<OrchestratorRunResult> {
    const envelope = this.contextGuard.createEnvelope(request);
    const requestedWorkers = normalizeRequestedWorkers(request.requestedWorkers);
    const agents = this.resolveAgents(requestedWorkers);

    const outcome = await this.executor.execute(envelope, agents);
    const report = createExecutionReport(
      envelope.request.runId,
      envelope.request.baseRef,
      envelope.request.executionSeed,
      requestedWorkers,
      envelope.normalizedFeatureFlags,
      outcome.results,
      this.hasher,
    );
    const reportHash = hashExecutionReport(report, this.hasher);

    return {
      report,
      reportHash,
      results: outcome.results,
      trace: outcome.trace,
    };
  }

  private resolveAgents(workerIds: readonly WorkerId[]): readonly FactoryAgent[] {
    const agents: FactoryAgent[] = [];
    for (const workerId of workerIds) {
      if (!this.registry.has(workerId)) {
        throw new Error(`Requested worker ${workerId} is not registered.`);
      }
      agents.push(this.registry.get(workerId));
    }
    return agents;
  }
}
