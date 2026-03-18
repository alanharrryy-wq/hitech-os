import { useMemo, useSyncExternalStore } from "react";
import { type InspectorCapabilityContext, type SelectionStoreSnapshot } from "./contracts";
import { deriveInspectorTarget } from "./inspector-target";
import { type SelectionStore } from "./selection-store";

export function useSelectionSnapshot(store: SelectionStore): SelectionStoreSnapshot {
  return useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
}

export function useInspectorTarget(store: SelectionStore, capabilityContext: InspectorCapabilityContext) {
  const snapshot = useSelectionSnapshot(store);
  return useMemo(() => deriveInspectorTarget(snapshot.selection, capabilityContext), [snapshot, capabilityContext]);
}
