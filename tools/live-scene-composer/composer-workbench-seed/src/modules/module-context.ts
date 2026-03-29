import type {
  CommandLike,
  ModuleContextLike,
  MutationIntent,
  MutationResult,
  RuntimeRouteStatus,
  SelectionState,
  Unsubscribe,
} from "../contracts";
import { CommandDispatcher } from "../core/command-dispatcher";
import { EventBus } from "../core/event-bus";
import { ServiceContainer } from "../core/service-container";

export interface ModuleContextOptions {
  readonly moduleId: string;
  readonly eventBus: EventBus;
  readonly dispatcher: CommandDispatcher;
  readonly serviceContainer: ServiceContainer;
  readonly readSelection: () => SelectionState;
  readonly requestMutation: (intent: MutationIntent) => Promise<MutationResult>;
  readonly getRuntimeRouteStatus: () => RuntimeRouteStatus;
}

export class ModuleContext implements ModuleContextLike {
  public readonly moduleId: string;

  private readonly eventBus: EventBus;
  private readonly dispatcher: CommandDispatcher;
  private readonly serviceContainer: ServiceContainer;
  private readonly readSelectionFn: () => SelectionState;
  private readonly requestMutationFn: (
    intent: MutationIntent,
  ) => Promise<MutationResult>;
  private readonly routeStatusFn: () => RuntimeRouteStatus;

  public constructor(options: ModuleContextOptions) {
    this.moduleId = options.moduleId;
    this.eventBus = options.eventBus;
    this.dispatcher = options.dispatcher;
    this.serviceContainer = options.serviceContainer;
    this.readSelectionFn = options.readSelection;
    this.requestMutationFn = options.requestMutation;
    this.routeStatusFn = options.getRuntimeRouteStatus;
  }

  public getService<T = unknown>(name: string): T | undefined {
    return this.serviceContainer.get<T>(name);
  }

  public requireService<T = unknown>(name: string): T {
    return this.serviceContainer.require<T>(name);
  }

  public registerCommand(name: string, command: CommandLike): void {
    this.dispatcher.register(name, command);
  }

  public unregisterCommand(name: string): void {
    this.dispatcher.unregister(name);
  }

  public subscribeEvent<TPayload = unknown>(
    event: string,
    handler: (payload: TPayload) => void,
  ): Unsubscribe {
    return this.eventBus.subscribe(event, handler);
  }

  public emitEvent<TPayload = unknown>(event: string, payload?: TPayload): void {
    this.eventBus.publish(event, payload);
  }

  public readSelection(): SelectionState {
    return this.readSelectionFn();
  }

  public requestMutation(intent: MutationIntent): Promise<MutationResult> {
    return this.requestMutationFn(intent);
  }

  public getRuntimeRouteStatus(): RuntimeRouteStatus {
    return this.routeStatusFn();
  }
}
