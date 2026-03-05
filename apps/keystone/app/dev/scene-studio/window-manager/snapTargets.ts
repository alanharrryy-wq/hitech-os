import type { SnapTarget, ViewportBounds } from "./types";

export interface SnapTargetOptions {
  readonly padding?: number;
  readonly includeThreeByThree?: boolean;
}

export const DEFAULT_SNAP_PADDING = 12;

function createGridTargets(
  viewport: ViewportBounds,
  columns: number,
  rows: number,
  padding: number,
  labelPrefix: string
): SnapTarget[] {
  const width = Math.max(viewport.width - padding * 2, 120);
  const height = Math.max(viewport.height - padding * 2, 120);
  const cellWidth = Math.floor(width / columns);
  const cellHeight = Math.floor(height / rows);

  const targets: SnapTarget[] = [];

  for (let col = 0; col < columns; col += 1) {
    for (let row = 0; row < rows; row += 1) {
      const x = padding + col * cellWidth;
      const y = padding + row * cellHeight;
      const w = col === columns - 1 ? width - cellWidth * col : cellWidth;
      const h = row === rows - 1 ? height - cellHeight * row : cellHeight;

      targets.push({
        x,
        y,
        w,
        h,
        kind: "grid",
        label: `${labelPrefix}-${col + 1}-${row + 1}`
      });
    }
  }

  return targets;
}

export function buildEdgeTargets(viewport: ViewportBounds, padding = DEFAULT_SNAP_PADDING): SnapTarget[] {
  const width = Math.max(viewport.width - padding * 2, 120);
  const height = Math.max(viewport.height - padding * 2, 120);
  const halfWidth = Math.floor(width / 2);
  const halfHeight = Math.floor(height / 2);

  return [
    { x: padding, y: padding, w: halfWidth, h: height, kind: "edge", label: "edge-left" },
    {
      x: padding + halfWidth,
      y: padding,
      w: width - halfWidth,
      h: height,
      kind: "edge",
      label: "edge-right"
    },
    { x: padding, y: padding, w: width, h: halfHeight, kind: "edge", label: "edge-top" },
    {
      x: padding,
      y: padding + halfHeight,
      w: width,
      h: height - halfHeight,
      kind: "edge",
      label: "edge-bottom"
    }
  ];
}

export function buildGridTargets(viewport: ViewportBounds, options?: SnapTargetOptions): SnapTarget[] {
  const padding = Math.max(options?.padding ?? DEFAULT_SNAP_PADDING, 0);
  const includeThreeByThree = Boolean(options?.includeThreeByThree);

  const twoByTwo = createGridTargets(viewport, 2, 2, padding, "grid-2x2");

  if (!includeThreeByThree) {
    return twoByTwo;
  }

  return [...twoByTwo, ...createGridTargets(viewport, 3, 3, padding, "grid-3x3")];
}
