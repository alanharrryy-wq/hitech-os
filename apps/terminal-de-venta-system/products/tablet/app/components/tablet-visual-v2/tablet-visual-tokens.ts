export const PRISMA_TABLET_VISUAL_V2 = {
  name: "PRISMA Softglass Terminal V2",
  dataAttribute: "PRISMA_SOFTGLASS_TERMINAL_V2",
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
    pearl: "#fbfdff",
    mist: "#eaf2fa",
    frost: "rgba(255, 255, 255, 0.74)",
    softSilver: "#cdd9e7",
    cyan: "#34d6ff",
    blue: "#2f82ff",
    lavender: "#9b8cff",
    champagne: "#ead7a2",
    graphite: "#142033"
  },
  scale: {
    radiusControl: "clamp(16px, 1.8vw, 24px)",
    radiusPanel: "clamp(22px, 2.4vw, 34px)",
    panelPadding: "clamp(14px, 2vw, 26px)",
    shellGap: "clamp(10px, 1.5vw, 18px)"
  }
} as const;

export type PrismaTabletVisualV2Token = typeof PRISMA_TABLET_VISUAL_V2;
