export const TABLET_VISUAL_V2_MOTION_RECIPES = {
  modalEnter: { durationMs: 220, easing: "cubic-bezier(0.22, 1, 0.36, 1)", properties: ["opacity", "transform"] },
  modalExit: { durationMs: 160, easing: "ease", properties: ["opacity", "transform"] },
  cardPress: { durationMs: 140, easing: "ease-out", properties: ["transform", "box-shadow"] },
  dockItemActive: { durationMs: 180, easing: "cubic-bezier(0.22, 1, 0.36, 1)", properties: ["transform", "box-shadow"] },
  liquidButtonHover: { durationMs: 180, easing: "cubic-bezier(0.22, 1, 0.36, 1)", properties: ["transform", "box-shadow"] },
  liquidButtonPress: { durationMs: 120, easing: "ease-out", properties: ["transform"] },
  ticketTotalPulse: { durationMs: 540, easing: "ease-out", properties: ["box-shadow", "opacity"] },
  productAddedEcho: { durationMs: 420, easing: "ease-out", properties: ["transform", "opacity"] },
  methodSelectedGlow: { durationMs: 220, easing: "ease-out", properties: ["border-color", "box-shadow"] },
  surfaceBreathingGlow: { durationMs: 6800, easing: "ease-in-out", properties: ["opacity", "transform"] },
  successSweep: { durationMs: 680, easing: "cubic-bezier(0.22, 1, 0.36, 1)", properties: ["transform", "opacity"] }
} as const;

export const TABLET_VISUAL_V2_REDUCED_MOTION_RULE = "prefers-reduced-motion: reduce disables transform animations and looping glow.";
