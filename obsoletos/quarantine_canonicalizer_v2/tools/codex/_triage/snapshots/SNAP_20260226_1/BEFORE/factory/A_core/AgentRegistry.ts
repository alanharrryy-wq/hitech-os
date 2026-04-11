import {
  AgentRegistrationRecord,
  FactoryAgent,
  assertFactoryAgent,
} from "../contracts/AgentInterface";
import {
  FACTORY_BLOCK_SEQUENCE,
  WorkerId,
  assertWorkerId,
} from "../contracts/FactoryContracts";

export interface AgentRegistryOptions {
  readonly allowReplace?: boolean;
  readonly fixedOrder?: readonly WorkerId[];
}

function buildOrderIndex(order: readonly WorkerId[]): Readonly<Record<string, number>> {
  const index: Record<string, number> = {};
  for (const [position, workerId] of order.entries()) {
    index[workerId] = position;
  }
  return index;
}

export class AgentRegistry {
  private readonly agentsById: Map<WorkerId, FactoryAgent>;
  private readonly orderIndex: Readonly<Record<string, number>>;
  private readonly allowReplace: boolean;

  constructor(options: AgentRegistryOptions = {}) {
    this.agentsById = new Map<WorkerId, FactoryAgent>();
    this.allowReplace = options.allowReplace ?? false;
    const fixedOrder = options.fixedOrder ?? FACTORY_BLOCK_SEQUENCE;
    this.orderIndex = buildOrderIndex(fixedOrder);
  }

  register(agent: FactoryAgent): void {
    assertFactoryAgent(agent, "agent");
    const alreadyRegistered = this.agentsById.has(agent.workerId);
    if (alreadyRegistered && !this.allowReplace) {
      throw new Error(`Worker ${agent.workerId} is already registered.`);
    }

    this.agentsById.set(agent.workerId, agent);
  }

  unregister(workerId: WorkerId): boolean {
    assertWorkerId(workerId, "workerId");
    return this.agentsById.delete(workerId);
  }

  get(workerId: WorkerId): FactoryAgent {
    assertWorkerId(workerId, "workerId");
    const agent = this.agentsById.get(workerId);
    if (agent === undefined) {
      throw new Error(`Worker ${workerId} is not registered.`);
    }
    return agent;
  }

  has(workerId: WorkerId): boolean {
    assertWorkerId(workerId, "workerId");
    return this.agentsById.has(workerId);
  }

  size(): number {
    return this.agentsById.size;
  }

  list(): readonly FactoryAgent[] {
    const agents = Array.from(this.agentsById.values());
    return agents.sort((left, right) => this.compareAgents(left, right));
  }

  listRegistrations(): readonly AgentRegistrationRecord[] {
    return this.list().map((agent) => ({
      workerId: agent.workerId,
      deterministicOrderHint: agent.deterministicOrderHint,
      description: agent.description,
    }));
  }

  private compareAgents(left: FactoryAgent, right: FactoryAgent): number {
    const leftFixedIndex = this.orderIndex[left.workerId];
    const rightFixedIndex = this.orderIndex[right.workerId];

    if (leftFixedIndex !== undefined && rightFixedIndex !== undefined && leftFixedIndex !== rightFixedIndex) {
      return leftFixedIndex - rightFixedIndex;
    }
    if (leftFixedIndex !== undefined && rightFixedIndex === undefined) {
      return -1;
    }
    if (leftFixedIndex === undefined && rightFixedIndex !== undefined) {
      return 1;
    }
    if (left.deterministicOrderHint !== right.deterministicOrderHint) {
      return left.deterministicOrderHint - right.deterministicOrderHint;
    }
    return left.workerId.localeCompare(right.workerId);
  }
}
