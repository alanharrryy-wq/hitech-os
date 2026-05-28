/**
 * PRISMA Surface Visual Governor - Surface Runtime Adapter V1
 * Surface: tablet
 * Consumption bridge only. It does not apply visual recipes by itself.
 */

export type PrismaSurfaceRuntimeDecision = {
  allowed: boolean;
  surface: string;
  route: string;
  mode: "inactive" | "preview" | "validated";
  reason: string;
  budget: {
    lightFirst: boolean;
    touchFirst: boolean;
    publicSober: boolean;
    posSafe: boolean;
    allowAtmosphereAssets: boolean;
    allowHeavyBlur: boolean;
    allowWebgl: boolean;
    allowPixi: boolean;
    allowDarkStorm: boolean;
  };
};

const SURFACE = "tablet";

export function evaluatePrismaSurfaceRuntime(route: string): PrismaSurfaceRuntimeDecision {
  const normalizedRoute = route || "/";
  const isPos = normalizedRoute.startsWith("/pos");
  const isCheckout = normalizedRoute.startsWith("/checkout");
  const isTablet = SURFACE === "tablet";
  const isMobile = SURFACE === "mobile";

  return {
    allowed: true,
    surface: SURFACE,
    route: normalizedRoute,
    mode: "validated",
    reason: "Pilot 17 adapter exposes governed recipe consumption without applying styles automatically.",
    budget: {
      lightFirst: isTablet || isMobile || isPos || isCheckout,
      touchFirst: isTablet || isMobile || isPos || isCheckout,
      publicSober: SURFACE === "web",
      posSafe: isPos || isCheckout,
      allowAtmosphereAssets: true,
      allowHeavyBlur: !(isTablet || isMobile || isPos || isCheckout),
      allowWebgl: false,
      allowPixi: false,
      allowDarkStorm: !(isTablet || isMobile || isPos || isCheckout),
    },
  };
}

export function getPrismaSurfaceRuntimeManifestUrl(): string {
  return "/surface-visual-governor/runtime-adapter/latest/index.json";
}
