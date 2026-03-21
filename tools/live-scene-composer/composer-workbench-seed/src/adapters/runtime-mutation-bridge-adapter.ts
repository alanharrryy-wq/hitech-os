import type {
  MutationIntent,
  MutationResult,
  RuntimeMutationBridgeAdapterContract,
  RuntimeRouteStatus,
} from "../contracts";

export interface RuntimeMutationBridgeAdapterOptions {
  readonly workspaceId: string;
  readonly bridgeRoute?: string;
  readonly safeMode?: boolean;
}

export class RuntimeMutationBridgeAdapter
  implements RuntimeMutationBridgeAdapterContract
{
  public readonly routeName: string;
  public readonly isStub = true;

  private readonly status: RuntimeRouteStatus;

  public constructor(options: RuntimeMutationBridgeAdapterOptions) {
    this.routeName = options.bridgeRoute ?? "runtime-mutation-bridge/stub";

    this.status = {
      safeMode: options.safeMode ?? true,
      bridgeRoute: this.routeName,
      workspaceId: options.workspaceId,
      workspaceState: "idle",
    };
  }

  public getRouteStatus(): RuntimeRouteStatus {
    return { ...this.status };
  }

  public async preview(intent: MutationIntent): Promise<MutationResult> {
    // TODO(live bridge): route preview to real runtime-mutation-bridge adapter.
    return {
      accepted: true,
      route: this.routeName,
      summary: `preview accepted in stub for '${intent.type}'`,
      diagnostics: [
        "adapter is a stub",
        "no runtime writes were performed",
        "replace with bridge adapter implementation for connected mode",
      ],
    };
  }

  public async commit(intent: MutationIntent): Promise<MutationResult> {
    // TODO(live bridge): commit must remain adapter-routed and policy-checked.
    return {
      accepted: false,
      route: this.routeName,
      summary: `commit blocked in safe stub for '${intent.type}'`,
      diagnostics: [
        "adapter is in safe mode",
        "direct runtime writes are intentionally disabled",
        "bridge adapter implementation is deferred by architecture boundary",
      ],
    };
  }
}
