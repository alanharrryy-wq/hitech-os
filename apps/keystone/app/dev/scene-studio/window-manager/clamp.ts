import type { ViewportBounds, WindowGeometry, WindowLayout, WindowLayoutEntry } from "./types";

export const DEFAULT_WINDOW_PADDING = 12;
export const DEFAULT_MIN_WIDTH = 280;
export const DEFAULT_MIN_HEIGHT = 140;

function normalizeNumber(value: number, fallback: number): number {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  return Math.round(value);
}

function clampValue(value: number, min: number, max: number): number {
  if (value < min) {
    return min;
  }

  if (value > max) {
    return max;
  }

  return value;
}

export function getViewportBounds(): ViewportBounds {
  if (typeof window === "undefined") {
    return { width: 1440, height: 900 };
  }

  return {
    width: Math.max(window.innerWidth, 320),
    height: Math.max(window.innerHeight, 320)
  };
}

export function clampGeometry(
  input: WindowGeometry,
  viewport: ViewportBounds,
  options?: {
    readonly padding?: number;
    readonly minWidth?: number;
    readonly minHeight?: number;
  }
): WindowGeometry {
  const padding = Math.max(options?.padding ?? DEFAULT_WINDOW_PADDING, 0);
  const minWidth = Math.max(options?.minWidth ?? DEFAULT_MIN_WIDTH, 120);
  const minHeight = Math.max(options?.minHeight ?? DEFAULT_MIN_HEIGHT, 72);

  const maxWidth = Math.max(viewport.width - padding * 2, minWidth);
  const maxHeight = Math.max(viewport.height - padding * 2, minHeight);

  const width = clampValue(normalizeNumber(input.w, minWidth), minWidth, maxWidth);
  const height = clampValue(normalizeNumber(input.h, minHeight), minHeight, maxHeight);

  const minX = padding;
  const minY = padding;
  const maxX = Math.max(viewport.width - padding - width, minX);
  const maxY = Math.max(viewport.height - padding - height, minY);

  return {
    x: clampValue(normalizeNumber(input.x, minX), minX, maxX),
    y: clampValue(normalizeNumber(input.y, minY), minY, maxY),
    w: width,
    h: height
  };
}

export function clampWindowEntry(
  input: WindowLayoutEntry,
  viewport: ViewportBounds,
  options?: {
    readonly padding?: number;
    readonly minWidth?: number;
    readonly minHeight?: number;
  }
): WindowLayoutEntry {
  const geometry = clampGeometry(input, viewport, options);

  return {
    ...input,
    ...geometry,
    z: Number.isFinite(input.z) ? Math.round(input.z) : 1000,
    visible: Boolean(input.visible),
    collapsed: Boolean(input.collapsed)
  };
}

export function clampLayout(
  layout: WindowLayout,
  viewport: ViewportBounds,
  options?: {
    readonly padding?: number;
    readonly minWidth?: number;
    readonly minHeight?: number;
  }
): WindowLayout {
  const windows = Object.fromEntries(
    Object.entries(layout.windows).map(([id, entry]) => [id, clampWindowEntry(entry, viewport, options)])
  );

  return {
    ...layout,
    windows
  };
}
