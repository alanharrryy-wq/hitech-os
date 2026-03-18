export const safeModeAllowed = [
  "scene-look-update",
  "layout-move",
  "layout-resize",
  "widget-props-update",
  "widget-style-update",
  "widget-remove",
  "draft-discard",
  "draft-commit",
  "selected-element-reset"
] as const;

export function safeModeAllows(type: string): boolean {
  return safeModeAllowed.includes(type as (typeof safeModeAllowed)[number]);
}
