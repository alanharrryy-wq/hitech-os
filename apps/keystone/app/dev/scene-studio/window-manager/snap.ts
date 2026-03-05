import { clampGeometry } from "./clamp";
import { buildEdgeTargets, buildGridTargets, DEFAULT_SNAP_PADDING } from "./snapTargets";
import type { SnapCandidate, ViewportBounds, WindowGeometry } from "./types";

export const DEFAULT_SNAP_THRESHOLD = 20;

export interface SnapComputationInput {
  readonly rect: WindowGeometry;
  readonly pointer: { readonly x: number; readonly y: number };
  readonly viewport: ViewportBounds;
  readonly threshold?: number;
  readonly padding?: number;
  readonly disableSnap?: boolean;
  readonly forceGrid?: boolean;
  readonly includeThreeByThree?: boolean;
}

function distanceToTargetCenter(
  pointer: SnapComputationInput["pointer"],
  target: { readonly x: number; readonly y: number; readonly w: number; readonly h: number }
): number {
  const centerX = target.x + target.w / 2;
  const centerY = target.y + target.h / 2;
  return Math.hypot(pointer.x - centerX, pointer.y - centerY);
}

function pickClosestTarget(
  pointer: SnapComputationInput["pointer"],
  targets: readonly { readonly x: number; readonly y: number; readonly w: number; readonly h: number; readonly kind: "edge" | "grid"; readonly label: string }[]
): SnapCandidate | null {
  if (targets.length === 0) {
    return null;
  }

  let selected: SnapCandidate | null = null;

  for (const target of targets) {
    const score = distanceToTargetCenter(pointer, target);
    if (!selected || score < selected.score) {
      selected = {
        ...target,
        score
      };
    }
  }

  return selected;
}

export function computeSnapCandidate(input: SnapComputationInput): SnapCandidate | null {
  const threshold = Math.max(input.threshold ?? DEFAULT_SNAP_THRESHOLD, 4);
  const padding = Math.max(input.padding ?? DEFAULT_SNAP_PADDING, 0);

  if (input.disableSnap) {
    return null;
  }

  const edgeTargets = buildEdgeTargets(input.viewport, padding);
  const gridTargets = buildGridTargets(input.viewport, {
    padding,
    ...(input.includeThreeByThree !== undefined ? { includeThreeByThree: input.includeThreeByThree } : {})
  });

  if (input.forceGrid) {
    return pickClosestTarget(input.pointer, gridTargets);
  }

  const edgeCandidates = edgeTargets.filter((target) => {
    if (target.label === "edge-left") {
      return input.pointer.x <= padding + threshold;
    }

    if (target.label === "edge-right") {
      return input.pointer.x >= input.viewport.width - padding - threshold;
    }

    if (target.label === "edge-top") {
      return input.pointer.y <= padding + threshold;
    }

    if (target.label === "edge-bottom") {
      return input.pointer.y >= input.viewport.height - padding - threshold;
    }

    return false;
  });

  const edgeSnap = pickClosestTarget(input.pointer, edgeCandidates);
  if (edgeSnap) {
    return edgeSnap;
  }

  const centerX = input.viewport.width / 2;
  const centerY = input.viewport.height / 2;
  const closeToCenterLines =
    Math.abs(input.pointer.x - centerX) <= threshold || Math.abs(input.pointer.y - centerY) <= threshold;

  if (!closeToCenterLines) {
    return null;
  }

  return pickClosestTarget(input.pointer, gridTargets);
}

export function applySnapCandidate(
  candidate: SnapCandidate,
  viewport: ViewportBounds,
  options?: {
    readonly minWidth?: number;
    readonly minHeight?: number;
    readonly padding?: number;
  }
): WindowGeometry {
  return clampGeometry(
    {
      x: candidate.x,
      y: candidate.y,
      w: candidate.w,
      h: candidate.h
    },
    viewport,
    options
  );
}
