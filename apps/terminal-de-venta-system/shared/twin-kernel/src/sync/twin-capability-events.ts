import { SHARED_SYNC_EVENTS, type SharedSyncEvent } from "./events";
import { TWIN_CAPABILITY_MANIFEST } from "../data/twin-capability-manifest";
import type { TwinSurface } from "../types/capability";

export type TwinRuntimeEventDescriptor = {
  name: SharedSyncEvent;
  capabilities: string[];
  requiredBy: string[];
  producedBy: TwinSurface[];
  consumedBy: TwinSurface[];
};

function unique<T>(values: T[]): T[] {
  return [...new Set(values)];
}

export function buildTwinRuntimeEventCatalog(): TwinRuntimeEventDescriptor[] {
  return SHARED_SYNC_EVENTS.map((eventName) => {
    const refs = TWIN_CAPABILITY_MANIFEST.flatMap((capability) =>
      capability.events
        .filter((eventRef) => eventRef.name === eventName)
        .map((eventRef) => ({ capability, eventRef }))
    );
    return {
      name: eventName,
      capabilities: refs.map((ref) => ref.capability.id),
      requiredBy: refs.filter((ref) => ref.eventRef.required).map((ref) => ref.capability.id),
      producedBy: unique(refs.flatMap((ref) => ref.eventRef.producedBy)),
      consumedBy: unique(refs.flatMap((ref) => ref.eventRef.consumedBy))
    };
  });
}

export const TWIN_RUNTIME_EVENT_CATALOG = buildTwinRuntimeEventCatalog();
