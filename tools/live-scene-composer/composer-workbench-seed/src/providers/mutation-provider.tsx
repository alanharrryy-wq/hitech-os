import type {
  MutationIntent,
  MutationResult,
  RuntimeMutationBridgeAdapterContract,
  RuntimeRouteStatus,
} from "../contracts";
import { EventBus, WorkbenchEvents } from "../core/event-bus";

export interface MutationRecord {
  readonly intent: MutationIntent;
  readonly result: MutationResult;
  readonly atUtc: string;
}

export class MutationProvider {
  private readonly history: MutationRecord[] = [];

  public constructor(
    private readonly adapter: RuntimeMutationBridgeAdapterContract,
    private readonly eventBus?: EventBus,
  ) {}

  public async requestMutation(intent: MutationIntent): Promise<MutationResult> {
    this.eventBus?.publish(WorkbenchEvents.MUTATION_REQUESTED, intent);

    const result = intent.dryRun
      ? await this.adapter.preview(intent)
      : await this.adapter.commit(intent);

    this.history.push({
      intent,
      result,
      atUtc: new Date().toISOString(),
    });

    this.eventBus?.publish(WorkbenchEvents.MUTATION_RESULT, {
      intent,
      result,
    });

    return result;
  }

  public getHistory(): readonly MutationRecord[] {
    return this.history.slice();
  }

  public getRouteStatus(): RuntimeRouteStatus {
    return this.adapter.getRouteStatus();
  }
}
