export const TABLET_VISUAL_V2_LAYERS = {
  base: 0,
  surface: 10,
  header: 20,
  content: 30,
  ticket: 40,
  dock: 80,
  popover: 120,
  modalBackdrop: 300,
  modal: 320,
  toast: 360,
  debug: 900
} as const;

export const TABLET_VISUAL_V2_LAYER_RULES = [
  "modalBackdrop > dock",
  "modal > modalBackdrop",
  "modal > popover",
  "dock > header",
  "dock > content",
  "toast > modal",
  "debug is reserved for diagnostics only"
] as const;

export function getTabletVisualV2Layer(name: keyof typeof TABLET_VISUAL_V2_LAYERS) {
  return TABLET_VISUAL_V2_LAYERS[name];
}
