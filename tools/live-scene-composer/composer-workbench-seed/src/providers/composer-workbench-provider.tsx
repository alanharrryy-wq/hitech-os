import type {
  ModuleRegistration,
  ModuleRuntimeSnapshot,
  MutationIntent,
  MutationResult,
  RuntimeMutationBridgeAdapterContract,
  RuntimeRouteStatus,
  SelectionState,
} from "../contracts";
import { RuntimeMutationBridgeAdapter } from "../adapters/runtime-mutation-bridge-adapter";
import { CommandDispatcher } from "../core/command-dispatcher";
import { EventBus, WorkbenchEvents } from "../core/event-bus";
import { ServiceContainer } from "../core/service-container";
import { ModuleContext } from "../modules/module-context";
import { ModuleLoader, type ModuleLoadReport } from "../modules/module-loader";
import { ModuleRegistry } from "../modules/module-registry";
import { MutationProvider } from "./mutation-provider";
import { SelectionProvider } from "./selection-provider";

export interface ComposerWorkbenchProviderOptions {
  readonly workspaceId: string;
  readonly moduleRegistrations?: readonly ModuleRegistration[];
  readonly bridgeAdapter?: RuntimeMutationBridgeAdapterContract;
  readonly initialSelection?: SelectionState;
}

export class ComposerWorkbenchProvider {
  public readonly serviceContainer = new ServiceContainer();
  public readonly eventBus = new EventBus();
  public readonly commandDispatcher = new CommandDispatcher();
  public readonly moduleRegistry = new ModuleRegistry();

  public readonly selectionProvider: SelectionProvider;
  public readonly mutationProvider: MutationProvider;
  public readonly moduleLoader: ModuleLoader;

  private workspaceState: RuntimeRouteStatus["workspaceState"] = "idle";

  public constructor(private readonly options: ComposerWorkbenchProviderOptions) {
    const adapter =
      options.bridgeAdapter ??
      new RuntimeMutationBridgeAdapter({
        workspaceId: options.workspaceId,
      });

    this.selectionProvider = new SelectionProvider(
      options.initialSelection,
      this.eventBus,
    );
    this.mutationProvider = new MutationProvider(adapter, this.eventBus);

    this.moduleLoader = new ModuleLoader({
      registry: this.moduleRegistry,
      createContext: (moduleId) =>
        new ModuleContext({
          moduleId,
          eventBus: this.eventBus,
          dispatcher: this.commandDispatcher,
          serviceContainer: this.serviceContainer,
          readSelection: () => this.selectionProvider.getSelection(),
          requestMutation: (intent: MutationIntent) =>
            this.mutationProvider.requestMutation(intent),
          getRuntimeRouteStatus: () => this.getRouteStatus(),
        }),
    });

    this.registerCoreServices();

    for (const registration of options.moduleRegistrations ?? []) {
      this.registerModule(registration);
    }
  }

  public registerModule(registration: ModuleRegistration): void {
    this.moduleRegistry.register(registration);
    this.eventBus.publish(WorkbenchEvents.MODULE_REGISTERED, {
      moduleId: registration.manifest.id,
      owner: registration.manifest.owner,
    });
  }

  public async initializeModules(): Promise<ModuleLoadReport> {
    const report = await this.moduleLoader.initializeAll();
    this.workspaceState = report.failed.length === 0 ? "ready" : "degraded";
    return report;
  }

  public async shutdownModules(): Promise<void> {
    await this.moduleLoader.shutdownAll();
    this.workspaceState = "idle";
  }

  public getRouteStatus(): RuntimeRouteStatus {
    const base = this.mutationProvider.getRouteStatus();
    return {
      ...base,
      workspaceState: this.workspaceState,
    };
  }

  public getModuleSnapshots(): readonly ModuleRuntimeSnapshot[] {
    return this.moduleRegistry.listRuntimeSnapshots();
  }

  public getSelection(): SelectionState {
    return this.selectionProvider.getSelection();
  }

  public requestMutation(intent: MutationIntent): Promise<MutationResult> {
    return this.mutationProvider.requestMutation(intent);
  }

  private registerCoreServices(): void {
    this.serviceContainer.register("event_bus", this.eventBus);
    this.serviceContainer.register("command_dispatcher", this.commandDispatcher);
    this.serviceContainer.register("module_registry", this.moduleRegistry);
    this.serviceContainer.register("selection_provider", this.selectionProvider);
    this.serviceContainer.register("mutation_provider", this.mutationProvider);
  }
}
