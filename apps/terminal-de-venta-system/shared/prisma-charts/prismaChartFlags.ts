import type { PrismaChartFlags, PrismaChartSurface } from "./prismaChartContracts";

type SearchParamsLike = Record<string, string | string[] | undefined>;

function envEnabled(name: string) {
  return process.env[name] === "true" || process.env[`NEXT_PUBLIC_${name}`] === "true";
}

function paramValue(searchParams: SearchParamsLike | undefined, key: string) {
  const value = searchParams?.[key];
  return Array.isArray(value) ? value[0] : value;
}

export function resolvePrismaChartFlags(surface: PrismaChartSurface, searchParams?: SearchParamsLike): PrismaChartFlags {
  const previewEnabled = paramValue(searchParams, "preview") === "charts" || paramValue(searchParams, "charts") === "1";
  const masterEnabled = envEnabled("PRISMA_CHARTS_ENABLED");
  const surfaceEnabled = envEnabled(`PRISMA_CHARTS_${surface.toUpperCase()}`);
  const useMockFallback = process.env.PRISMA_CHARTS_MOCKS_FALLBACK !== "false";
  const enabled = previewEnabled || (masterEnabled && surfaceEnabled);
  return {
    enabled,
    masterEnabled,
    surfaceEnabled,
    previewEnabled,
    useMockFallback,
    reason: enabled ? "Preview or feature flag enabled." : "Feature flags are off by default. Use ?preview=charts for safe preview."
  };
}

