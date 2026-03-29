import {
  type BridgeDecision,
  type BridgeAdapterRequest,
  type MutationEnvelope
} from "./contracts";
import { type BridgeAdapter, selectAdapter, InMemoryBridgeAdapter } from "./bridge-adapter";

export interface BridgeClient {
  readonly adapters: readonly BridgeAdapter[];
  send(request: BridgeAdapterRequest): Promise<BridgeDecision>;
}

export class DefaultBridgeClient implements BridgeClient {
  public readonly adapters: readonly BridgeAdapter[];

  public constructor(adapters: readonly BridgeAdapter[] = [new InMemoryBridgeAdapter()]) {
    this.adapters = adapters;
  }

  public async send(request: BridgeAdapterRequest): Promise<BridgeDecision> {
    const adapter = selectAdapter(this.adapters, request.envelope);
    if (!adapter) {
      return {
        accepted: false,
        decisionKind: request.action === "commit" ? "commit-rejected" : "preview-rejected",
        mutationId: request.envelope.mutationId,
        reason: "No adapter available for request envelope.",
        diagnostics: ["adapter-unavailable"]
      };
    }
    const result = await adapter.handle(request);
    return {
      accepted: result.accepted,
      decisionKind: translateDecisionKind(request.action, result.accepted),
      mutationId: request.envelope.mutationId,
      reason: result.accepted ? undefined : "Adapter rejected request.",
      adapterKey: result.adapterKey,
      diagnostics: result.diagnostics
    };
  }
}

function translateDecisionKind(action: BridgeAdapterRequest["action"], accepted: boolean): BridgeDecision["decisionKind"] {
  if (action === "discard") {
    return "discard-approved";
  }
  if (action === "revert") {
    return "revert-approved";
  }
  if (action === "commit") {
    return accepted ? "commit-approved" : "commit-rejected";
  }
  return accepted ? "preview-approved" : "preview-rejected";
}

export async function requestBridgePreview(client: BridgeClient, envelope: MutationEnvelope): Promise<BridgeDecision> {
  return client.send({ envelope, action: "preview" });
}

export async function requestBridgeCommit(client: BridgeClient, envelope: MutationEnvelope): Promise<BridgeDecision> {
  return client.send({ envelope, action: "commit" });
}

export async function requestBridgeDiscard(client: BridgeClient, envelope: MutationEnvelope): Promise<BridgeDecision> {
  return client.send({ envelope, action: "discard" });
}

export async function requestBridgeRevert(client: BridgeClient, envelope: MutationEnvelope): Promise<BridgeDecision> {
  return client.send({ envelope, action: "revert" });
}
