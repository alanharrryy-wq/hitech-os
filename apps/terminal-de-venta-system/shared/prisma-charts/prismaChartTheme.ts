// PHASE4_EXECUTIVE_COMMAND_CENTER_PRO_V1
import type { PrismaOperationalStatus, PrismaSeverity } from "./prismaChartContracts";
import { prismaChartIntentPalette, prismaChartPremiumTokens, prismaChartLuxuryTokens, type PrismaChartIntentPreset } from "./prismaChartTokens";

type ChartOption = Record<string, unknown>;
type UnknownRecord = Record<string, unknown>;

export const prismaChartTokens = {
  /** Executive Observatory: calm, dark, legible. */
  bg: "#050914",
  bgDeep: "#02040b",
  panel: "rgba(9, 16, 30, 0.88)",
  panelSoft: "rgba(13, 23, 40, 0.76)",
  panelStrong: "rgba(6, 12, 24, 0.96)",
  ink: "#e8eef7",
  inkStrong: "#f8fbff",
  inkMuted: "#9aaabd",
  inkFaint: "#66778d",
  line: "rgba(157, 177, 204, 0.14)",
  lineStrong: "rgba(157, 177, 204, 0.28)",
  grid: "rgba(157, 177, 204, 0.105)",
  axis: "rgba(157, 177, 204, 0.28)",
  tooltip: "rgba(5, 10, 20, 0.96)",
  tooltipBorder: "rgba(142, 202, 255, 0.24)",
  electricBlue: "#4f8cff",
  cyan: "#63dfff",
  silver: "#d7e3f2",
  green: "#35d49b",
  amber: "#f2b94b",
  red: "#ff5f72",
  violet: "#a78bfa",
  blueDim: "#1b3b6d",
  cyanDim: "#155266",
  greenDim: "#17543d",
  amberDim: "#6a4c17",
  redDim: "#651f2d",
  shadow: "0 24px 70px rgba(0, 0, 0, 0.42), 0 0 48px rgba(79, 140, 255, 0.08)",
  focusRing: "0 0 0 3px rgba(99, 223, 255, 0.16), 0 0 0 1px rgba(99, 223, 255, 0.42)"
} as const;

export type PrismaChartTone = "info" | "success" | "warning" | "danger" | "violet" | "neutral";

export const prismaChartTonePalette: Record<PrismaChartTone, string> = {
  info: prismaChartTokens.cyan,
  success: prismaChartTokens.green,
  warning: prismaChartTokens.amber,
  danger: prismaChartTokens.red,
  violet: prismaChartTokens.violet,
  neutral: prismaChartTokens.inkMuted
};

const executivePalette = [
  prismaChartTokens.electricBlue,
  prismaChartTokens.cyan,
  prismaChartTokens.green,
  prismaChartTokens.amber,
  prismaChartTokens.red,
  prismaChartTokens.violet,
  prismaChartTokens.silver
] as const;

const quietHeatRamp = [
  prismaChartTokens.blueDim,
  prismaChartTokens.cyanDim,
  prismaChartTokens.green,
  prismaChartTokens.amber,
  prismaChartTokens.red
] as const;

export function chartText() {
  return prismaChartTokens.ink;
}

export function chartTextStrong() {
  return prismaChartTokens.inkStrong;
}

export function chartMuted() {
  return prismaChartTokens.inkMuted;
}

export function chartFaint() {
  return prismaChartTokens.inkFaint;
}

export function chartGrid() {
  return prismaChartTokens.grid;
}

export function chartAxis() {
  return prismaChartTokens.axis;
}

export function chartPanel() {
  return prismaChartTokens.panel;
}

export function chartTooltip() {
  return prismaChartTokens.tooltip;
}

export function getSeriesPalette(kind: "executive" | "heat" | "status" = "executive") {
  if (kind === "heat") return [...quietHeatRamp];
  if (kind === "status") return [prismaChartTokens.green, prismaChartTokens.amber, prismaChartTokens.red, prismaChartTokens.cyan, prismaChartTokens.violet];
  return [...executivePalette];
}

export function severityColor(severity: PrismaSeverity | string) {
  const normalized = String(severity).toUpperCase();
  if (normalized === "CRITICAL") return prismaChartTokens.red;
  if (normalized === "ERROR" || normalized === "HIGH") return "#ff8a6b";
  if (normalized === "WARN" || normalized === "WARNING" || normalized === "MEDIUM") return prismaChartTokens.amber;
  if (normalized === "LOW") return prismaChartTokens.green;
  return prismaChartTokens.cyan;
}

export function statusColor(status: PrismaOperationalStatus | string) {
  const normalized = String(status).toUpperCase();
  if (normalized === "PASS" || normalized === "FRESH" || normalized === "HIGH" || normalized === "LIVE" || normalized === "SUCCESS") return prismaChartTokens.green;
  if (normalized === "DEGRADED" || normalized === "WARN" || normalized === "WARNING" || normalized === "AGING" || normalized === "MEDIUM" || normalized === "PARTIAL") return prismaChartTokens.amber;
  if (normalized === "FAIL" || normalized === "CRITICAL" || normalized === "ERROR" || normalized === "LOW" || normalized === "STALE") return prismaChartTokens.red;
  if (normalized === "OFFLINE" || normalized === "UNKNOWN") return prismaChartTokens.inkFaint;
  return prismaChartTokens.inkMuted;
}

export function densityColor(state: string | undefined, pressureScore: number) {
  if (state === "anomaly") return prismaChartTokens.red;
  if (state === "peak") return prismaChartTokens.amber;
  if (state === "cold") return prismaChartTokens.blueDim;
  if (pressureScore >= 88) return prismaChartTokens.red;
  if (pressureScore >= 76) return prismaChartTokens.amber;
  if (pressureScore >= 58) return prismaChartTokens.violet;
  if (pressureScore >= 36) return prismaChartTokens.cyan;
  return prismaChartTokens.blueDim;
}

export const prismaEchartsTheme = {
  color: executivePalette,
  backgroundColor: "transparent",
  textStyle: {
    color: prismaChartTokens.ink,
    fontFamily: "Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif",
    fontWeight: 650
  },
  title: {
    textStyle: { color: prismaChartTokens.inkStrong, fontWeight: 850 },
    subtextStyle: { color: prismaChartTokens.inkMuted }
  },
  legend: {
    textStyle: { color: prismaChartTokens.inkMuted, fontWeight: 700 },
    itemGap: 16
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: prismaChartTokens.axis } },
    axisTick: { lineStyle: { color: prismaChartTokens.axis } },
    axisLabel: { color: prismaChartTokens.inkMuted, fontWeight: 700 },
    splitLine: { lineStyle: { color: prismaChartTokens.grid } }
  },
  valueAxis: {
    axisLine: { lineStyle: { color: prismaChartTokens.axis } },
    axisTick: { lineStyle: { color: prismaChartTokens.axis } },
    axisLabel: { color: prismaChartTokens.inkMuted, fontWeight: 700 },
    splitLine: { lineStyle: { color: prismaChartTokens.grid } }
  }
};

const colorAliases: Record<string, string> = {
  "#071426": prismaChartTokens.ink,
  "#0b1728": prismaChartTokens.panelStrong,
  "#66738a": prismaChartTokens.inkMuted,
  "#93a4ba": prismaChartTokens.inkMuted,
  "#d8e1ec": prismaChartTokens.silver,
  "#eaf2ff": prismaChartTokens.blueDim,
  "#eef4fb": prismaChartTokens.bg,
  "#ffffff": prismaChartTokens.inkStrong,
  "#fff": prismaChartTokens.inkStrong,
  "#f8fafc": prismaChartTokens.inkStrong,
  "#086dff": prismaChartTokens.electricBlue,
  "#63dfff": prismaChartTokens.cyan,
  "#13b981": prismaChartTokens.green,
  "#13f5a3": prismaChartTokens.green,
  "#22f7a6": prismaChartTokens.green,
  "#e59b2a": prismaChartTokens.amber,
  "#f4c542": prismaChartTokens.amber,
  "#df3d2f": prismaChartTokens.red,
  "#ff4f5e": prismaChartTokens.red,
  "#7557ff": prismaChartTokens.violet,
  "#7c5cff": prismaChartTokens.violet,
  "#b46cff": prismaChartTokens.violet
};

const rgbaAliases: Record<string, string> = {
  "rgba(255,255,255,0.82)": prismaChartTokens.panelSoft,
  "rgba(255,255,255,0.94)": prismaChartTokens.panelStrong,
  "rgba(255,255,255,.82)": "rgba(232, 238, 247, 0.72)",
  "rgba(255,255,255,.80)": "rgba(232, 238, 247, 0.68)",
  "rgba(255,255,255,.78)": "rgba(232, 238, 247, 0.62)",
  "rgba(255,255,255,.74)": "rgba(232, 238, 247, 0.58)",
  "rgba(7,20,38,.94)": prismaChartTokens.tooltip,
  "rgba(7, 20, 38, 0.86)": "rgba(5, 10, 20, 0.90)",
  "rgba(7, 20, 38, 0.9)": "rgba(5, 10, 20, 0.92)",
  "rgba(255, 255, 255, 0.94)": prismaChartTokens.panelSoft,
  "rgba(255, 255, 255, 0.42)": "rgba(232, 238, 247, 0.08)",
  "rgba(112, 144, 176, 0.28)": prismaChartTokens.axis,
  "rgba(112, 144, 176, 0.15)": prismaChartTokens.grid,
  "rgba(134,154,184,.22)": prismaChartTokens.grid,
  "rgba(102,115,138,.72)": prismaChartTokens.inkMuted
};

function normalizeColorToken(value: string) {
  const trimmed = value.trim();
  const lower = trimmed.toLowerCase();
  if (colorAliases[lower]) return colorAliases[lower];
  if (rgbaAliases[trimmed]) return rgbaAliases[trimmed];
  return value;
}

function isPlainObject(value: unknown): value is UnknownRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function normalizePrismaChartOption<T>(input: T): T {
  if (typeof input === "string") return normalizeColorToken(input) as T;
  if (Array.isArray(input)) return input.map((item) => normalizePrismaChartOption(item)) as T;
  if (!isPlainObject(input)) return input;

  const normalized: UnknownRecord = {};
  for (const [key, value] of Object.entries(input)) {
    normalized[key] = normalizePrismaChartOption(value);
  }
  return normalized as T;
}

function deepMerge(base: unknown, patch: unknown): unknown {
  if (Array.isArray(base) || Array.isArray(patch)) return patch ?? base;
  if (!isPlainObject(base) || !isPlainObject(patch)) return patch ?? base;
  const out: UnknownRecord = { ...base };
  for (const [key, value] of Object.entries(patch)) out[key] = deepMerge(out[key], value);
  return out;
}


function hasAxis(option: ChartOption, axisName: "xAxis" | "yAxis") {
  return option[axisName] !== undefined;
}

function hasSeriesKind(option: ChartOption, kind: string) {
  const series = option.series;
  const list = Array.isArray(series) ? series : series ? [series] : [];
  return list.some((item) => isPlainObject(item) && item.type === kind);
}

function inferIntentPreset(title: string, option: ChartOption): PrismaChartIntentPreset {
  const normalized = title.toLowerCase();
  if (hasSeriesKind(option, "heatmap") || normalized.includes("freshness") || normalized.includes("risk")) return "riskHeatmap";
  if (hasSeriesKind(option, "graph") || normalized.includes("dependency")) return "dependencyGraph";
  if (hasSeriesKind(option, "sankey") || normalized.includes("flow") || normalized.includes("sync")) return "syncFlow";
  if (hasSeriesKind(option, "line") || normalized.includes("timeline") || normalized.includes("lifecycle")) return "operationalTimeline";
  if (normalized.includes("quality") || normalized.includes("confidence")) return "qualityTrend";
  return "executiveMetric";
}

function premiumToolbox(title: string): ChartOption {
  return {
    show: true,
    right: 16,
    top: 12,
    itemSize: 15,
    itemGap: 10,
    iconStyle: {
      borderColor: prismaChartTokens.inkMuted,
      color: "rgba(8,15,28,.72)"
    },
    emphasis: {
      iconStyle: {
        borderColor: prismaChartTokens.cyan,
        color: "rgba(99,223,255,.12)"
      }
    },
    feature: {
      restore: { title: "Restore" },
      saveAsImage: {
        title: "Export PNG",
        name: title.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase() || "prisma-chart",
        backgroundColor: prismaChartPremiumTokens.export.background,
        pixelRatio: prismaChartPremiumTokens.export.pixelRatio
      }
    }
  };
}

function premiumDataZoom(option: ChartOption): ChartOption[] | undefined {
  if (!hasAxis(option, "xAxis")) return undefined;
  if (hasSeriesKind(option, "heatmap") || hasSeriesKind(option, "graph") || hasSeriesKind(option, "sankey") || hasSeriesKind(option, "treemap")) return undefined;
  return [
    {
      type: "inside",
      throttle: 56,
      zoomOnMouseWheel: "ctrl",
      moveOnMouseMove: true,
      moveOnMouseWheel: true
    },
    {
      type: "slider",
      height: 16,
      bottom: 10,
      borderColor: prismaChartPremiumTokens.depth.hairline,
      backgroundColor: "rgba(99,223,255,.045)",
      fillerColor: "rgba(99,223,255,.13)",
      handleStyle: { color: prismaChartTokens.cyan, borderColor: prismaChartTokens.cyan },
      textStyle: { color: prismaChartTokens.inkFaint },
      showDetail: false
    }
  ];
}

function premiumBrush(option: ChartOption): ChartOption | undefined {
  if (!hasAxis(option, "xAxis") || hasSeriesKind(option, "treemap") || hasSeriesKind(option, "sankey")) return undefined;
  return {
    toolbox: ["rect", "lineX", "clear"],
    xAxisIndex: "all",
    brushMode: "single",
    throttleType: "debounce",
    throttleDelay: 160,
    brushStyle: {
      borderWidth: 1,
      color: prismaChartPremiumTokens.interaction.brushFill,
      borderColor: prismaChartPremiumTokens.interaction.brushStroke
    }
  };
}

function premiumSeries(series: unknown): unknown {
  if (Array.isArray(series)) return series.map((item) => premiumSeries(item));
  if (!isPlainObject(series)) return series;
  const type = typeof series.type === "string" ? series.type : "";
  const emphasis = deepMerge(
    {
      focus: type === "graph" || type === "sankey" ? "adjacency" : "series",
      blurScope: "coordinateSystem"
    },
    series.emphasis
  );
  const blur = deepMerge(
    {
      itemStyle: { opacity: 0.34 },
      lineStyle: { opacity: 0.25 },
      areaStyle: { opacity: 0.18 }
    },
    series.blur
  );
  const select = deepMerge(
    {
      itemStyle: { borderColor: prismaChartTokens.cyan, borderWidth: 1 }
    },
    series.select
  );
  return {
    ...series,
    emphasis,
    blur,
    select,
    animationDelay: series.animationDelay ?? ((index: number) => Math.min(index * 12, 260)),
    animationDelayUpdate: series.animationDelayUpdate ?? ((index: number) => Math.min(index * 8, 180))
  };
}

export function applyExecutiveObservatoryPremium(title: string, option: ChartOption): ChartOption {
  const intent = inferIntentPreset(title, option);
  const palette = prismaChartIntentPalette[intent];
  const dataZoom = premiumDataZoom(option);
  const brush = premiumBrush(option);
  const premium: ChartOption = {
    color: [...palette],
    animation: true,
    animationDuration: prismaChartPremiumTokens.motion.cinematic.duration,
    animationDurationUpdate: prismaChartPremiumTokens.motion.calm.update,
    animationEasing: "cubicOut",
    animationEasingUpdate: "quarticOut",
    toolbox: premiumToolbox(title),
    stateAnimation: { duration: 260, easing: "cubicOut" },
    dataZoom,
    brush,
    series: premiumSeries(option.series)
  };
  if (!dataZoom) delete premium.dataZoom;
  if (!brush) delete premium.brush;
  return deepMerge(premium, option) as ChartOption;
}

export function basePrismaChartOption(title: string, description: string): ChartOption {
  return {
    backgroundColor: "transparent",
    animation: true,
    animationDuration: 620,
    animationDurationUpdate: 360,
    animationEasing: "cubicOut",
    animationEasingUpdate: "cubicOut",
    color: getSeriesPalette(),
    title: {
      show: false,
      text: title,
      subtext: description,
      textStyle: { color: chartTextStrong(), fontWeight: 850 },
      subtextStyle: { color: chartMuted(), fontWeight: 650 }
    },
    aria: {
      show: true,
      description
    },
    legend: {
      textStyle: { color: chartMuted(), fontWeight: 700 },
      itemGap: 16,
      itemWidth: 14,
      itemHeight: 8
    },
    tooltip: {
      trigger: "item",
      appendToBody: true,
      confine: true,
      enterable: true,
      transitionDuration: prismaChartLuxuryTokens.cadence.micro / 1000,
      borderWidth: 1,
      borderColor: prismaChartTokens.tooltipBorder,
      backgroundColor: chartTooltip(),
      padding: [10, 12],
      textStyle: { color: chartText(), fontWeight: 650 },
      extraCssText: "border-radius:16px;box-shadow:0 26px 90px rgba(0,0,0,.52);backdrop-filter:blur(22px);letter-spacing:.01em;"
    },
    textStyle: prismaEchartsTheme.textStyle
  };
}


export function applyLuxuryObservatoryPolish(title: string, option: ChartOption): ChartOption {
  const luxury: ChartOption = {
    backgroundColor: "transparent",
    axisPointer: {
      animation: true,
      snap: true,
      lineStyle: { color: prismaChartLuxuryTokens.affordance.rail, width: 1, type: "dashed" },
      label: {
        show: true,
        color: prismaChartTokens.inkStrong,
        backgroundColor: prismaChartTokens.panelStrong,
        borderColor: prismaChartTokens.tooltipBorder,
        borderWidth: 1,
        shadowBlur: 14,
        shadowColor: "rgba(0,0,0,.34)"
      }
    },
    graphic: [
      {
        type: "text",
        right: 16,
        bottom: 12,
        silent: true,
        invisible: true,
        style: {
          text: prismaChartLuxuryTokens.export.watermark,
          fill: prismaChartTokens.inkFaint,
          fontSize: 10,
          fontWeight: 700
        }
      }
    ],
    textStyle: {
      color: prismaChartTokens.ink,
      fontFamily: "Inter, SF Pro Display, Segoe UI, system-ui, sans-serif"
    }
  };
  return deepMerge(luxury, option) as ChartOption;
}

export function mergePrismaChartOption(title: string, description: string, option: ChartOption): ChartOption {
  const premiumOption = applyExecutiveObservatoryPremium(title, option);
  const luxuryOption = applyLuxuryObservatoryPolish(title, premiumOption);
  return normalizePrismaChartOption(deepMerge(basePrismaChartOption(title, description), luxuryOption) as ChartOption);
}
