
import { buildCanvasViewModel } from "./canvas-viewmodel";
import { type CoordinationEventRecord, type CoordinationSnapshot, type SceneGraphInput, type SelectionState, type SelectionStoreCompat, type SurfaceEvent, type SurfaceInstruction } from "./contracts";
import { pickBestCanvasHit } from "./pointer-hit-selection";
import { buildRecoverySuggestions, reconcileSelection } from "./stale-reconciliation";
import { buildStructureTreeProjection } from "./structure-tree-projection";

function nowUtc(): string {
  return new Date().toISOString();
}

export function createSurfaceCoordinator(input: { store: SelectionStoreCompat; scene: SceneGraphInput; observedBounds: readonly any[] }) {
  let records: CoordinationEventRecord[] = [];

  function derive(selection: SelectionState): CoordinationSnapshot {
    const reconciled = reconcileSelection(input.scene, selection);
    const tree = buildStructureTreeProjection(input.scene, reconciled);
    const canvas = buildCanvasViewModel({ scene: input.scene, selection: reconciled, bounds: input.observedBounds });
    const instructions: SurfaceInstruction[] = [];

    if (reconciled.status === "none") {
      instructions.push(
        { surface: "structure-tree", action: "clear-active-node", ref: null, notes: ["No active selection."] },
        { surface: "canvas", action: "clear-overlays", ref: null, notes: ["No active selection."] },
        { surface: "inspector", action: "show-empty", ref: null, notes: ["No target."] }
      );
    } else if (reconciled.status === "stale") {
      instructions.push(
        { surface: "structure-tree", action: "show-stale-diagnostics", ref: reconciled.ref, notes: buildRecoverySuggestions(input.scene, reconciled).map((item) => item.label) },
        { surface: "canvas", action: "show-unavailable-overlay", ref: reconciled.ref, notes: [reconciled.staleReason ?? "stale"] },
        { surface: "inspector", action: "disable-editing", ref: reconciled.ref, notes: ["Selection stale."] }
      );
    } else {
      instructions.push(
        { surface: "structure-tree", action: "highlight-active-node", ref: reconciled.ref, notes: ["Synchronized active target."] },
        { surface: "canvas", action: "show-active-overlays", ref: reconciled.ref, notes: ["Use viewmodel overlays."] },
        { surface: "inspector", action: "show-derived-target", ref: reconciled.ref, notes: ["Selection remains active."] }
      );
    }

    return {
      selection: reconciled,
      tree,
      canvas,
      instructions,
      diagnostics: [
        `selection:${reconciled.status}`,
        `treeFlatOrder:${tree.flatOrder.length}`,
        `canvasOverlays:${canvas.overlays.length}`
      ]
    };
  }

  function record(event: SurfaceEvent, before: SelectionState, after: SelectionState, notes: readonly string[] = []): void {
    records = [
      ...records,
      { kind: event.kind, origin: event.origin, beforeStatus: before.status, afterStatus: after.status, atUtc: nowUtc(), notes }
    ];
  }

  return {
    getSnapshot(): CoordinationSnapshot {
      return derive(input.store.getSnapshot().selection);
    },

    dispatch(event: SurfaceEvent): CoordinationSnapshot {
      const before = input.store.getSnapshot().selection;
      switch (event.kind) {
        case "canvas-hit": {
          const candidates = (event.payload?.candidates as readonly any[]) ?? [];
          const ref = event.ref ?? pickBestCanvasHit(input.scene, candidates);
          if (ref && event.revision) {
            input.store.select({ ref, origin: "canvas", revision: event.revision, reason: event.reason ?? "surface-select" });
          }
          break;
        }
        case "tree-select": {
          if (event.ref && event.revision) {
            input.store.select({ ref: event.ref, origin: "structure-tree", revision: event.revision, reason: event.reason ?? "surface-select" });
          }
          break;
        }
        case "canvas-clear": {
          input.store.clear(event.reason ?? "clear-selection", "canvas");
          break;
        }
        case "entity-removed":
        case "revision-replaced":
        case "sync-refresh": {
          input.store.markStale(event.reason ?? event.kind, event.revision);
          break;
        }
        case "explicit-recovery": {
          if (event.ref && event.revision) {
            input.store.select({ ref: event.ref, origin: "system", revision: event.revision, reason: "explicit-recovery" });
          }
          break;
        }
        case "tree-focus-move":
        case "tree-toggle-expand": {
          break;
        }
      }
      const after = derive(input.store.getSnapshot().selection).selection;
      record(event, before, after);
      return this.getSnapshot();
    },

    getEventLog(): readonly CoordinationEventRecord[] {
      return records;
    }
  };
}
