export const prismaChartSemanticTokens = {
  status: {
    live: "#35d49b",
    partial: "#f2b94b",
    stale: "#ff5f72",
    offline: "#66778d",
    unknown: "#9aaabd"
  },
  risk: {
    critical: "#ff5f72",
    high: "#ff8a6b",
    medium: "#f2b94b",
    low: "#35d49b"
  },
  chart: {
    text: { primary: "#e8eef7", strong: "#f8fbff", muted: "#9aaabd", faint: "#66778d" },
    axis: { subtle: "rgba(157,177,204,.28)", label: "#9aaabd" },
    grid: { soft: "rgba(157,177,204,.105)" },
    line: { premium: "#63dfff", command: "#4f8cff" },
    area: { crystal: "rgba(99,223,255,.115)", obsidian: "rgba(9,16,30,.88)" },
    tooltip: { glass: "rgba(5,10,20,.96)", border: "rgba(142,202,255,.24)" },
    glow: { primary: "0 0 28px rgba(99,223,255,.14)", quiet: "0 24px 70px rgba(0,0,0,.42)" },
    point: { accent: "#f2b94b" }
  },
  surface: {
    pc: { background: "#050914", density: "governance" },
    tablet: { background: "#050914", density: "touch" },
    mobile: { background: "#050914", density: "compact" }
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
  | "chart.text.primary"
  | "chart.text.strong"
  | "chart.text.muted"
  | "chart.text.faint"
  | "chart.axis.subtle"
  | "chart.axis.label"
  | "chart.grid.soft"
  | "chart.line.premium"
  | "chart.line.command"
  | "chart.area.crystal"
  | "chart.area.obsidian"
  | "chart.tooltip.glass"
  | "chart.tooltip.border"
  | "chart.glow.primary"
  | "chart.glow.quiet"
  | "chart.point.accent"
  | "surface.pc.background"
  | "surface.tablet.background"
  | "surface.mobile.background";


export const prismaChartPremiumTokens = {
  /** Executive Observatory Premium System: restrained luxury, not arcade neon. */
  depth: {
    base: "rgba(3, 7, 16, 0.96)",
    raised: "rgba(8, 15, 28, 0.86)",
    floating: "rgba(12, 22, 38, 0.78)",
    hairline: "rgba(157,177,204,.13)",
    hairlineStrong: "rgba(157,177,204,.24)",
    halo: "0 26px 90px rgba(0,0,0,.46), 0 0 52px rgba(99,223,255,.07)",
    hoverHalo: "0 30px 110px rgba(0,0,0,.52), 0 0 72px rgba(99,223,255,.12)"
  },
  motion: {
    still: { animation: false, duration: 0, update: 0 },
    calm: { animation: true, duration: 520, update: 320 },
    cinematic: { animation: true, duration: 820, update: 460 }
  },
  interaction: {
    focusBorder: "rgba(99,223,255,.42)",
    focusGlow: "0 0 0 4px rgba(99,223,255,.10)",
    mutedSelection: "rgba(99,223,255,.09)",
    brushFill: "rgba(99,223,255,.14)",
    brushStroke: "rgba(99,223,255,.38)"
  },
  export: {
    background: "#050914",
    pixelRatio: 3
  }
} as const;

export type PrismaChartIntentPreset =
  | "executiveMetric"
  | "operationalTimeline"
  | "riskHeatmap"
  | "syncFlow"
  | "dependencyGraph"
  | "qualityTrend";

export const prismaChartIntentPalette: Record<PrismaChartIntentPreset, readonly string[]> = {
  executiveMetric: ["#63dfff", "#4f8cff", "#d7e3f2"],
  operationalTimeline: ["#4f8cff", "#63dfff", "#a78bfa", "#35d49b", "#f2b94b"],
  riskHeatmap: ["#10213a", "#155266", "#35d49b", "#f2b94b", "#ff8a6b", "#ff5f72"],
  syncFlow: ["#4f8cff", "#63dfff", "#35d49b", "#a78bfa"],
  dependencyGraph: ["#63dfff", "#a78bfa", "#f2b94b", "#ff5f72"],
  qualityTrend: ["#35d49b", "#63dfff", "#f2b94b", "#ff5f72"]
} as const;


export const prismaChartLuxuryTokens = {
  /** Executive Observatory Luxury Polish: presentation-grade finish, still restrained. */
  presentation: {
    backdrop: "radial-gradient(circle at 22% 0%, rgba(99,223,255,.105), transparent 34%), radial-gradient(circle at 82% 12%, rgba(167,139,250,.075), transparent 30%), #050914",
    spotlight: "linear-gradient(115deg, transparent 0%, rgba(255,255,255,.075) 42%, transparent 68%)",
    vignette: "radial-gradient(circle at 50% 44%, transparent 0%, rgba(0,0,0,.20) 72%, rgba(0,0,0,.44) 100%)",
    printBackground: "#050914"
  },
  affordance: {
    rail: "rgba(99,223,255,.42)",
    railMuted: "rgba(157,177,204,.18)",
    keycapBg: "rgba(255,255,255,.055)",
    keycapBorder: "rgba(157,177,204,.18)",
    liveDot: "#35d49b",
    inspectDot: "#63dfff"
  },
  cadence: {
    micro: 140,
    soft: 260,
    composed: 460,
    cinematic: 820
  },
  export: {
    watermark: "PRISMA Executive Observatory",
    safeInset: 24
  }
} as const;


export const prismaChartCommandCenterProTokens = {
  /** Phase 4 Executive Command Center Pro: layout and readout tokens. */
  surface: {
    obsidian: "rgba(2, 6, 14, .94)",
    commandPanel: "rgba(8, 16, 30, .82)",
    raisedPanel: "rgba(13, 24, 42, .78)",
    glassLine: "rgba(166, 190, 222, .16)",
    glassLineStrong: "rgba(166, 190, 222, .29)"
  },
  readout: {
    excellent: "#35d49b",
    stable: "#63dfff",
    watch: "#f2b94b",
    risk: "#ff5f72",
    neutral: "#9aaabd"
  },
  motion: {
    focusScale: 1.006,
    hoverLiftPx: -1,
    calmMs: 260,
    heroMs: 720
  },
  presentation: {
    focusShadow: "0 44px 140px rgba(0,0,0,.62), 0 0 0 1px rgba(99,223,255,.16), 0 0 92px rgba(99,223,255,.105)",
    executiveRailBackground: "linear-gradient(135deg, rgba(255,255,255,.07), rgba(255,255,255,.022))"
  }
} as const;
