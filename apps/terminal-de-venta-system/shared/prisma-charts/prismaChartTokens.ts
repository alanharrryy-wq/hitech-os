export const prismaChartSemanticTokens = {
  status: {
    live: "#13b981",
    partial: "#e59b2a",
    stale: "#f59e0b",
    offline: "#64748b",
    unknown: "#93a4ba"
  },
  risk: {
    critical: "#df3d2f",
    high: "#ff7d66",
    medium: "#e59b2a",
    low: "#13b981"
  },
  chart: {
    axis: { subtle: "rgba(102,115,138,.72)", label: "#071426" },
    grid: { soft: "rgba(134,154,184,.22)" },
    line: { premium: "#63dfff" },
    area: { crystal: "rgba(99,223,255,.16)" },
    tooltip: { glass: "rgba(7,20,38,.94)" },
    glow: { primary: "0 0 24px rgba(99,223,255,.28)" },
    point: { accent: "#e59b2a" }
  },
  surface: {
    pc: { background: "#eef4fb", density: "governance" },
    tablet: { background: "#071426", density: "touch" },
    mobile: { background: "#071426", density: "compact" }
  }
} as const;

export type PrismaChartTokenPath =
  | "status.live"
  | "status.partial"
  | "status.stale"
  | "status.offline"
  | "status.unknown"
  | "risk.critical"
  | "risk.high"
  | "risk.medium"
  | "risk.low"
  | "chart.axis.subtle"
  | "chart.grid.soft"
  | "chart.line.premium"
  | "chart.area.crystal"
  | "chart.tooltip.glass"
  | "chart.glow.primary"
  | "surface.pc.background"
  | "surface.tablet.background"
  | "surface.mobile.background";

