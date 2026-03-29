
import { useMemo } from "react";
import { type ObservedBoundsEntry, type SceneGraphInput, type SelectionState } from "./contracts";
import { buildCanvasViewModel } from "./canvas-viewmodel";
import { buildStructureTreeProjection } from "./structure-tree-projection";
import { summarizeMutationCapabilities } from "./mutation-intent-entrypoints";

export function useStructureTreeProjection(scene: SceneGraphInput, selection: SelectionState) {
  return useMemo(() => buildStructureTreeProjection(scene, selection), [scene, selection]);
}

export function useCanvasViewModel(scene: SceneGraphInput, selection: SelectionState, bounds: readonly ObservedBoundsEntry[]) {
  return useMemo(() => buildCanvasViewModel({ scene, selection, bounds }), [scene, selection, bounds]);
}

export function useMutationCapabilitySummary(selection: SelectionState) {
  return useMemo(() => summarizeMutationCapabilities(selection), [selection]);
}
