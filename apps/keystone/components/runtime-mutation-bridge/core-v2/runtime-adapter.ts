import type { BridgePhase, ValidationIssue } from "./mutation-result";
import type { RuntimeObservationSnapshot, SceneDocument, SelectionTarget } from "./scene-domain";

export interface RuntimeMutationBridgeEvent {
  readonly commandId: string;
  readonly commandType: string;
  readonly phase: BridgePhase;
  readonly sceneRevision: number;
  readonly changedTargets: readonly string[];
  readonly validationIssueCodes: readonly string[];
  readonly recordedAtIso: string;
}

export interface RuntimeMutationBridgePublishArgs {
  readonly commandId: string;
  readonly commandType: string;
  readonly phase: Exclude<BridgePhase, "rejection">;
  readonly changedTargets: readonly string[];
  readonly document: SceneDocument;
}

export interface RuntimeMutationBridgeRejectArgs {
  readonly commandId: string;
  readonly commandType: string;
  readonly phase: "rejection";
  readonly document: SceneDocument;
  readonly issues: readonly ValidationIssue[];
}

export interface RuntimeMutationBridgeAdapter {
  snapshot(document: SceneDocument): SceneDocument;
  publish(args: RuntimeMutationBridgePublishArgs): SceneDocument;
  reject(args: RuntimeMutationBridgeRejectArgs): void;
  observe(document: SceneDocument, selection: SelectionTarget | null): RuntimeObservationSnapshot;
  listEvents?(): readonly RuntimeMutationBridgeEvent[];
  clearEvents?(): void;
}
