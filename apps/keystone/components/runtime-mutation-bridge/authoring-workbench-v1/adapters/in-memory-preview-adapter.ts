import type { RuntimeMutationCommand } from "../contract";
import type { SceneDocument } from "../../../live-scene-composer/authoring-workbench-v1/authoring-workbench-contracts";

export interface RuntimeMutationBridgeAdapterEvent {
  readonly commandType: RuntimeMutationCommand["type"];
  readonly phase: "preview" | "draft-update" | "commit" | "discard" | "rejection";
  readonly sceneRevision: number;
  readonly recordedAtIso: string;
}

export interface RuntimeMutationBridgeAdapter {
  record(command: RuntimeMutationCommand, phase: RuntimeMutationBridgeAdapterEvent["phase"], document: SceneDocument): void;
  list(): readonly RuntimeMutationBridgeAdapterEvent[];
  clear(): void;
}

export function createInMemoryPreviewAdapter(): RuntimeMutationBridgeAdapter {
  const events: RuntimeMutationBridgeAdapterEvent[] = [];
  return {
    record(command, phase, document) {
      events.push({
        commandType: command.type,
        phase,
        sceneRevision: document.meta.revision,
        recordedAtIso: new Date().toISOString(),
      });
    },
    list() {
      return events;
    },
    clear() {
      events.length = 0;
    },
  };
}
