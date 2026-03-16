import type { RuntimeMutationBridgeAdapter, RuntimeMutationBridgeEvent, RuntimeMutationBridgePublishArgs, RuntimeMutationBridgeRejectArgs } from "./runtime-adapter";
import { cloneSceneDocument, createRuntimeObservationSnapshot } from "./scene-domain";

function createEventFromPublish(args: RuntimeMutationBridgePublishArgs): RuntimeMutationBridgeEvent {
  return {
    commandId: args.commandId,
    commandType: args.commandType,
    phase: args.phase,
    sceneRevision: args.document.meta.revision,
    changedTargets: args.changedTargets,
    validationIssueCodes: [],
    recordedAtIso: new Date().toISOString(),
  };
}

function createEventFromReject(args: RuntimeMutationBridgeRejectArgs): RuntimeMutationBridgeEvent {
  return {
    commandId: args.commandId,
    commandType: args.commandType,
    phase: args.phase,
    sceneRevision: args.document.meta.revision,
    changedTargets: [],
    validationIssueCodes: args.issues.map((issue) => issue.code),
    recordedAtIso: new Date().toISOString(),
  };
}

export function createInMemoryPreviewAdapter(): RuntimeMutationBridgeAdapter {
  const events: RuntimeMutationBridgeEvent[] = [];

  return {
    snapshot(document) {
      return cloneSceneDocument(document);
    },
    publish(args) {
      events.push(createEventFromPublish(args));
      return cloneSceneDocument(args.document);
    },
    reject(args) {
      events.push(createEventFromReject(args));
    },
    observe(document, selection) {
      return createRuntimeObservationSnapshot(document, selection);
    },
    listEvents() {
      return [...events];
    },
    clearEvents() {
      events.length = 0;
    },
  };
}
