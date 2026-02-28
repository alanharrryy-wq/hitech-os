export const FOCUS_RING_CLASS =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ui-focus))] focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--ui-surface-1))]";

export function withFocusRing(base: string): string {
  return `${base} ${FOCUS_RING_CLASS}`.trim();
}
