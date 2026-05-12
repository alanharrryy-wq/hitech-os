import type { PrismaOperationalStatus, PrismaSeverity } from "./prismaChartContracts";

export const prismaChartTokens = {
  ink: "#071426",
  inkMuted: "#66738a",
  panel: "rgba(255,255,255,0.82)",
  panelStrong: "rgba(255,255,255,0.94)",
  line: "rgba(23,45,78,0.14)",
  electricBlue: "#086dff",
  cyan: "#63dfff",
  silver: "#d8e1ec",
  green: "#13b981",
  amber: "#e59b2a",
  red: "#df3d2f",
  violet: "#7557ff",
  shadow: "0 24px 70px rgba(28,74,130,.12)"
} as const;

export const prismaEchartsTheme = {
  color: [
    prismaChartTokens.electricBlue,
    prismaChartTokens.cyan,
    prismaChartTokens.green,
    prismaChartTokens.amber,
    prismaChartTokens.red,
    prismaChartTokens.violet,
    "#93a4ba"
  ],
  backgroundColor: "transparent",
  textStyle: {
    color: prismaChartTokens.ink,
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif"
  }
};

export function severityColor(severity: PrismaSeverity) {
  if (severity === "CRITICAL") return prismaChartTokens.red;
  if (severity === "ERROR") return "#ff7d66";
  if (severity === "WARN") return prismaChartTokens.amber;
  return prismaChartTokens.electricBlue;
}

export function statusColor(status: PrismaOperationalStatus | string) {
  const normalized = status.toUpperCase();
  if (normalized === "PASS" || normalized === "FRESH" || normalized === "HIGH") return prismaChartTokens.green;
  if (normalized === "DEGRADED" || normalized === "WARN" || normalized === "AGING" || normalized === "MEDIUM") return prismaChartTokens.amber;
  if (normalized === "FAIL" || normalized === "CRITICAL" || normalized === "ERROR" || normalized === "LOW") return prismaChartTokens.red;
  return "#93a4ba";
}

export function basePrismaChartOption(title: string, description: string) {
  return {
    backgroundColor: "transparent",
    animationDuration: 650,
    animationEasing: "cubicOut",
    title: {
      show: false,
      text: title,
      subtext: description
    },
    aria: {
      show: true,
      description
    },
    tooltip: {
      trigger: "item",
      appendToBody: true,
      borderWidth: 0,
      backgroundColor: "rgba(7,20,38,.94)",
      textStyle: { color: "#fff" }
    },
    textStyle: prismaEchartsTheme.textStyle
  };
}

