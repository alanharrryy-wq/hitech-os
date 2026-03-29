export type LifecycleResult = void | Promise<void>;

export type Unsubscribe = () => void;

export type ModuleStatus =
  | "registered"
  | "initialized"
  | "disabled"
  | "failed"
  | "skipped";

export interface ModuleManifest {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly owner: string;
  readonly description: string;
  readonly dependencies: readonly string[];
  readonly enabledByDefault: boolean;
}

export interface ModuleRuntimeSnapshot {
  readonly id: string;
  readonly owner: string;
  readonly status: ModuleStatus;
  readonly dependencies: readonly string[];
  readonly message?: string;
}

export interface SelectionRef {
  readonly kind: "scene" | "layout-node" | "slot" | "widget";
  readonly sceneId: string;
  readonly entityId: string;
  readonly slotId?: string;
}

export interface SelectionState {
  readonly current: SelectionRef | null;
  readonly origin: string;
  readonly updatedAtUtc: string;
}

export interface MutationIntent {
  readonly mutationId: string;
  readonly type: string;
  readonly target: Readonly<Record<string, string>>;
  readonly payload: unknown;
  readonly requestedBy: string;
  readonly dryRun: boolean;
}

export interface MutationResult {
  readonly accepted: boolean;
  readonly route: string;
  readonly summary: string;
  readonly diagnostics: readonly string[];
}

export interface RuntimeRouteStatus {
  readonly safeMode: boolean;
  readonly bridgeRoute: string;
  readonly workspaceId: string;
  readonly workspaceState: "idle" | "ready" | "degraded";
}

export interface CommandLike<TResult = unknown> {
  execute(...args: readonly unknown[]): TResult;
  canExecute?(): boolean;
  onExecuteError?(error: unknown): void;
}

export interface ModuleContextLike {
  readonly moduleId: string;
  getService<T = unknown>(name: string): T | undefined;
  requireService<T = unknown>(name: string): T;
  registerCommand(name: string, command: CommandLike): void;
  unregisterCommand(name: string): void;
  subscribeEvent<TPayload = unknown>(
    event: string,
    handler: (payload: TPayload) => void,
  ): Unsubscribe;
  emitEvent<TPayload = unknown>(event: string, payload?: TPayload): void;
  readSelection(): SelectionState;
  requestMutation(intent: MutationIntent): Promise<MutationResult>;
  getRuntimeRouteStatus(): RuntimeRouteStatus;
}

export interface ModuleInstance {
  readonly manifest: ModuleManifest;
  initialize(context: ModuleContextLike): LifecycleResult;
  shutdown?(): LifecycleResult;
}

export interface ModuleRegistration {
  readonly manifest: ModuleManifest;
  create(): ModuleInstance;
}

export interface RuntimeMutationBridgeAdapterContract {
  readonly routeName: string;
  readonly isStub: boolean;
  getRouteStatus(): RuntimeRouteStatus;
  preview(intent: MutationIntent): Promise<MutationResult>;
  commit(intent: MutationIntent): Promise<MutationResult>;
}

export interface ModuleBoardItem {
  readonly moduleId: string;
  readonly owner: string;
  readonly status: ModuleStatus;
  readonly description: string;
  readonly message?: string;
}

export interface WorkbenchTopStrip {
  readonly safeModeLabel: string;
  readonly bridgeRoute: string;
  readonly workspaceStatus: string;
}

export interface WorkbenchLayoutModel {
  readonly topStrip: WorkbenchTopStrip;
  readonly leftColumn: readonly string[];
  readonly centerColumn: readonly string[];
  readonly rightColumn: readonly string[];
}
