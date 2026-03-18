import {
  type BridgeAdapterRequest,
  type BridgeAdapterResult,
  type MutationEnvelope
} from "./contracts";

export interface BridgeAdapter {
  readonly adapterKey: string;
  supports(envelope: MutationEnvelope): boolean;
  handle(request: BridgeAdapterRequest): Promise<BridgeAdapterResult>;
}

export class InMemoryBridgeAdapter implements BridgeAdapter {
  public readonly adapterKey: string;

  public constructor(adapterKey = "in-memory-bridge-adapter") {
    this.adapterKey = adapterKey;
  }

  public supports(): boolean {
    return true;
  }

  public async handle(request: BridgeAdapterRequest): Promise<BridgeAdapterResult> {
    const accepted = request.envelope.type !== "widget-remove" || request.envelope.mode === "advanced" || request.action !== "preview";
    return {
      accepted,
      adapterKey: this.adapterKey,
      diagnostics: [
        `adapter=${this.adapterKey}`,
        `action=${request.action}`,
        `type=${request.envelope.type}`,
        accepted ? "accepted" : "rejected"
      ],
      appliedRevision: accepted ? `${request.envelope.target.sceneId}-rev-applied` : undefined
    };
  }
}

export function selectAdapter(adapters: readonly BridgeAdapter[], envelope: MutationEnvelope): BridgeAdapter | null {
  return adapters.find((adapter) => adapter.supports(envelope)) ?? null;
}
