export const PRISMA_TABLET_VISUAL_V2 = {
  name: "PRISMA Nocturne Terminal V3",
  dataAttribute: "PRISMA_NOCTURNE_TERMINAL_V3",
  canonicalViewport: {
    width: 1180,
    height: 820,
    zoom: 0.75
  },
  responsiveZoomChecks: [0.35, 0.75, 1, 1.9],
  touchTargetPx: 48,
  bodyTextMinPx: 14,
  criticalLabelMinPx: 15,
  actionTextMinPx: 16,
  tokens: {
    night: "#030912",
    petroleum: "#0b2133",
    glass: "rgba(9, 28, 45, 0.58)",
    coldEdge: "rgba(154, 210, 255, 0.24)",
    cyan: "#34d6ff",
    blue: "#4d8dff",
    violet: "#9a8cff",
    success: "#63e6ad",
    ink: "#f4f9ff"
  },
  scale: {
    radiusControl: "clamp(16px, 1.8vw, 24px)",
    radiusPanel: "clamp(22px, 2.4vw, 34px)",
    panelPadding: "clamp(14px, 2vw, 26px)",
    shellGap: "clamp(10px, 1.5vw, 18px)"
  }
} as const;

export type PrismaTabletVisualV2Token = typeof PRISMA_TABLET_VISUAL_V2;
