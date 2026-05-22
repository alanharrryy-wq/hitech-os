// PRISMA_CHART_RADICAL_THEMES_V1
// Shared theme registry for Chart Lab and ECharts options.
// PC visual layer only. Tablet operation remains local-first and independent.

export type PrismaChartThemeId = "crystal-light" | "paper" | "calm-night" | "dense-noir";

export type PrismaChartTheme = {
  id: PrismaChartThemeId;
  label: string;
  mode: "light" | "dark";
  density: "airy" | "editorial" | "calm" | "dense";
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  grid: string;
  axis: string;
  accent: string;
  accent2: string;
  accent3: string;
  line: string;
  areaTop: string;
  areaBottom: string;
  pulse: string;
  statusOpen: string;
  statusResolved: string;
  statusProgress: string;
  statusBlocked: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
  zoomBg: string;
  zoomFill: string;
  zoomHandle: string;
  labelBg: string;
  labelBorder: string;
  radiusLg: number;
  radiusMd: number;
  lineWidth: number;
  smooth: number | boolean;
  labelDensity: "full" | "short" | "quiet" | "minimal";
  rippleScale: number;
  rippleNumber: number;
  shadowBlur: number;
  glow: string;
};

export const PRISMA_CHART_THEMES: Record<PrismaChartThemeId, PrismaChartTheme> = {
  "crystal-light": {
    id: "crystal-light",
    label: "Crystal Light",
    mode: "light",
    density: "airy",
    textPrimary: "#0a1830",
    textSecondary: "#38506d",
    textMuted: "#6a7a92",
    grid: "rgba(77,120,170,0.12)",
    axis: "rgba(77,120,170,0.22)",
    accent: "#0b78ff",
    accent2: "#63dfff",
    accent3: "#7557ff",
    line: "#63dfff",
    areaTop: "rgba(99,223,255,0.26)",
    areaBottom: "rgba(99,223,255,0.02)",
    pulse: "rgba(99,223,255,0.26)",
    statusOpen: "#e59b2a",
    statusResolved: "#13b981",
    statusProgress: "#7557ff",
    statusBlocked: "#df3d2f",
    tooltipBg: "rgba(255,255,255,0.94)",
    tooltipBorder: "rgba(99,223,255,0.26)",
    tooltipText: "#071426",
    zoomBg: "rgba(255,255,255,0.38)",
    zoomFill: "rgba(8,109,255,0.16)",
    zoomHandle: "#ffffff",
    labelBg: "rgba(255,255,255,0.76)",
    labelBorder: "rgba(99,223,255,0.20)",
    radiusLg: 24,
    radiusMd: 14,
    lineWidth: 3,
    smooth: 0.42,
    labelDensity: "full",
    rippleScale: 2.6,
    rippleNumber: 3,
    shadowBlur: 16,
    glow: "rgba(99,223,255,0.34)"
  },
  paper: {
    id: "paper",
    label: "Paper Editorial",
    mode: "light",
    density: "editorial",
    textPrimary: "#2b2115",
    textSecondary: "#5a4936",
    textMuted: "#8b7a67",
    grid: "rgba(92,73,44,0.10)",
    axis: "rgba(92,73,44,0.20)",
    accent: "#8f5f2d",
    accent2: "#c9a46a",
    accent3: "#6b5142",
    line: "#8f5f2d",
    areaTop: "rgba(201,164,106,0.24)",
    areaBottom: "rgba(201,164,106,0.02)",
    pulse: "rgba(143,95,45,0.16)",
    statusOpen: "#c47a1b",
    statusResolved: "#3f8b56",
    statusProgress: "#7c5db5",
    statusBlocked: "#b64533",
    tooltipBg: "rgba(255,251,246,0.96)",
    tooltipBorder: "rgba(140,112,70,0.18)",
    tooltipText: "#2b2115",
    zoomBg: "rgba(255,247,238,0.52)",
    zoomFill: "rgba(143,95,45,0.14)",
    zoomHandle: "#fff8f1",
    labelBg: "rgba(255,250,244,0.82)",
    labelBorder: "rgba(92,73,44,0.12)",
    radiusLg: 18,
    radiusMd: 10,
    lineWidth: 2,
    smooth: 0.18,
    labelDensity: "short",
    rippleScale: 1.9,
    rippleNumber: 2,
    shadowBlur: 8,
    glow: "rgba(201,164,106,0.18)"
  },
  "calm-night": {
    id: "calm-night",
    label: "Calm Night",
    mode: "dark",
    density: "calm",
    textPrimary: "#e7f0fb",
    textSecondary: "#b1c0d4",
    textMuted: "#7e93ab",
    grid: "rgba(117,153,196,0.12)",
    axis: "rgba(117,153,196,0.18)",
    accent: "#40a9ff",
    accent2: "#38e1ff",
    accent3: "#61a0ff",
    line: "#38e1ff",
    areaTop: "rgba(56,225,255,0.18)",
    areaBottom: "rgba(56,225,255,0.01)",
    pulse: "rgba(56,225,255,0.22)",
    statusOpen: "#f3b45a",
    statusResolved: "#2ed39a",
    statusProgress: "#8e79ff",
    statusBlocked: "#ff6a63",
    tooltipBg: "rgba(14,20,33,0.96)",
    tooltipBorder: "rgba(56,225,255,0.20)",
    tooltipText: "#eef6ff",
    zoomBg: "rgba(26,40,60,0.82)",
    zoomFill: "rgba(64,169,255,0.18)",
    zoomHandle: "#d9e9f9",
    labelBg: "rgba(14,20,33,0.82)",
    labelBorder: "rgba(56,225,255,0.14)",
    radiusLg: 24,
    radiusMd: 14,
    lineWidth: 3,
    smooth: 0.36,
    labelDensity: "quiet",
    rippleScale: 2.35,
    rippleNumber: 3,
    shadowBlur: 18,
    glow: "rgba(56,225,255,0.26)"
  },
  "dense-noir": {
    id: "dense-noir",
    label: "Dense Noir",
    mode: "dark",
    density: "dense",
    textPrimary: "#f7f8fb",
    textSecondary: "#b7bfd0",
    textMuted: "#7e8698",
    grid: "rgba(145,153,181,0.10)",
    axis: "rgba(145,153,181,0.16)",
    accent: "#7557ff",
    accent2: "#29d3ff",
    accent3: "#ff4fd8",
    line: "#7557ff",
    areaTop: "rgba(117,87,255,0.22)",
    areaBottom: "rgba(117,87,255,0.01)",
    pulse: "rgba(117,87,255,0.22)",
    statusOpen: "#ffb44d",
    statusResolved: "#31d0a2",
    statusProgress: "#7557ff",
    statusBlocked: "#ff5c74",
    tooltipBg: "rgba(12,14,22,0.96)",
    tooltipBorder: "rgba(117,87,255,0.22)",
    tooltipText: "#f8fbff",
    zoomBg: "rgba(19,22,32,0.88)",
    zoomFill: "rgba(117,87,255,0.22)",
    zoomHandle: "#e4e7f1",
    labelBg: "rgba(12,14,22,0.76)",
    labelBorder: "rgba(117,87,255,0.16)",
    radiusLg: 16,
    radiusMd: 10,
    lineWidth: 4,
    smooth: 0.52,
    labelDensity: "minimal",
    rippleScale: 3.15,
    rippleNumber: 4,
    shadowBlur: 24,
    glow: "rgba(117,87,255,0.30)"
  }
};

const THEME_ALIASES: Record<string, PrismaChartThemeId> = {
  crystal: "crystal-light",
  light: "crystal-light",
  "crystal-light": "crystal-light",
  "crystal light": "crystal-light",
  paper: "paper",
  editorial: "paper",
  calm: "calm-night",
  night: "calm-night",
  "calm-night": "calm-night",
  "calm night": "calm-night",
  dense: "dense-noir",
  noir: "dense-noir",
  "dense-noir": "dense-noir",
  "dense noir": "dense-noir",
  "executive-dense": "dense-noir",
  "executive dense": "dense-noir"
};

export function normalizePrismaChartThemeId(value: unknown): PrismaChartThemeId {
  if (typeof value !== "string") return "crystal-light";
  const normalized = value.trim().toLowerCase().replace(/_/g, "-");
  return THEME_ALIASES[normalized] ?? "crystal-light";
}

export function prismaChartTheme(value: unknown): PrismaChartTheme {
  return PRISMA_CHART_THEMES[normalizePrismaChartThemeId(value)];
}
