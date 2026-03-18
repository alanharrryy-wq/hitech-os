import {
  type SelectionActiveState,
  type SelectionInput,
  type SelectionRecoveryInput,
  type SelectionReason,
  type SelectionState,
  type SelectionStoreClock,
  type SelectionStoreListener,
  type SelectionStoreOptions,
  type SelectionStoreSnapshot,
  assertValidSelectionState,
  createActiveSelection,
  createNoSelection,
  createStaleSelection,
  isActiveSelection,
  isStaleSelection,
  selectionRefToKey
} from "./contracts";

class SystemClock implements SelectionStoreClock {
  nowUtc(): string {
    return new Date().toISOString();
  }
}

function freezeSnapshot(snapshot: SelectionStoreSnapshot): SelectionStoreSnapshot {
  return Object.freeze({
    ...snapshot,
    selection: Object.freeze(snapshot.selection),
    lastTransition: snapshot.lastTransition ? Object.freeze(snapshot.lastTransition) : null
  });
}

export interface SelectionStore {
  getSnapshot(): SelectionStoreSnapshot;
  subscribe(listener: SelectionStoreListener): () => void;
  select(input: SelectionInput): SelectionStoreSnapshot;
  clear(reason?: SelectionReason, origin?: SelectionInput["origin"]): SelectionStoreSnapshot;
  markStale(reason: SelectionReason, revision?: string): SelectionStoreSnapshot;
  recover(input: SelectionRecoveryInput): SelectionStoreSnapshot;
  replaceRevision(nextRevision: string, resolver?: (current: SelectionActiveState) => boolean): SelectionStoreSnapshot;
  clearIfMatchesRef(refKey: string, reason?: SelectionReason): SelectionStoreSnapshot;
}

export function createSelectionStore(options: SelectionStoreOptions = {}): SelectionStore {
  const clock = options.clock ?? new SystemClock();
  const listeners = new Set<SelectionStoreListener>();
  let version = 0;
  let selection = options.initialSelection ?? createNoSelection();
  assertValidSelectionState(selection);
  let snapshot = freezeSnapshot({
    selection,
    version,
    lastTransition: null,
    updatedAtUtc: clock.nowUtc()
  });

  function commit(nextSelection: SelectionState, reason: SelectionReason, origin: SelectionInput["origin"]): SelectionStoreSnapshot {
    assertValidSelectionState(nextSelection);
    const previousStatus = snapshot.selection.status;
    version += 1;
    snapshot = freezeSnapshot({
      selection: nextSelection,
      version,
      lastTransition: {
        version,
        previousStatus,
        nextStatus: nextSelection.status,
        reason,
        origin,
        atUtc: clock.nowUtc()
      },
      updatedAtUtc: clock.nowUtc()
    });
    for (const listener of [...listeners]) {
      listener(snapshot);
    }
    return snapshot;
  }

  return {
    getSnapshot(): SelectionStoreSnapshot {
      return snapshot;
    },

    subscribe(listener: SelectionStoreListener): () => void {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },

    select(input: SelectionInput): SelectionStoreSnapshot {
      const next = createActiveSelection(input);
      return commit(next, input.reason ?? "surface-select", input.origin);
    },

    clear(reason = "clear-selection", origin = "system"): SelectionStoreSnapshot {
      return commit(createNoSelection(), reason, origin);
    },

    markStale(reason: SelectionReason, revision?: string): SelectionStoreSnapshot {
      const current = snapshot.selection;
      if (current.status === "none") {
        return snapshot;
      }
      if (isStaleSelection(current) && current.staleReason === reason && (!revision || current.revision === revision)) {
        return snapshot;
      }
      const stale = createStaleSelection(current, reason, revision ?? current.revision);
      return commit(stale, reason, current.origin);
    },

    recover(input: SelectionRecoveryInput): SelectionStoreSnapshot {
      const next = createActiveSelection({
        ref: input.ref,
        origin: input.origin,
        revision: input.revision,
        context: input.context,
        reason: input.recoveryReason
      });
      return commit(next, input.recoveryReason, input.origin);
    },

    replaceRevision(nextRevision: string, resolver?: (current: SelectionActiveState) => boolean): SelectionStoreSnapshot {
      const current = snapshot.selection;
      if (!isActiveSelection(current)) {
        return snapshot;
      }
      if (current.revision === nextRevision) {
        return snapshot;
      }
      const stillValid = resolver ? resolver(current) : false;
      if (stillValid) {
        return commit({ ...current, revision: nextRevision }, "revision-replaced", current.origin);
      }
      return this.markStale("revision-replaced", nextRevision);
    },

    clearIfMatchesRef(refKey: string, reason = "entity-removed"): SelectionStoreSnapshot {
      const current = snapshot.selection;
      if (current.status === "none") {
        return snapshot;
      }
      if (selectionRefToKey(current.ref) !== refKey) {
        return snapshot;
      }
      if (isActiveSelection(current)) {
        return commit(createStaleSelection(current, reason), reason, current.origin);
      }
      return commit(createNoSelection(), reason, current.origin);
    }
  };
}
