#!/usr/bin/env node
/**
 * PRISMA Surface Visual Governor - Route Recipe Runtime Adapter V1
 * Shared contract helper. No dependencies. No UI mutation.
 */

export const ADAPTER_VERSION = "1.0.0-pilot-17";

export function normalizeRouteBudget(input = {}) {
  const surface = String(input.surface || "unknown");
  const route = String(input.route || "/");
  const isPos = route.startsWith("/pos");
  const isCheckout = route.startsWith("/checkout");
  const isTablet = surface === "tablet";
  const isMobile = surface === "mobile";
  const isPublic = surface === "web" || surface === "eit_web";

  return {
    surface,
    route,
    allowed: true,
    adapterVersion: ADAPTER_VERSION,
    markers: ["surface-runtime-adapter", "route-budget-enforcer", "governed-consumption"],
    budget: {
      lightFirst: isTablet || isMobile || isPos || isCheckout || isPublic,
      touchFirst: isTablet || isMobile || isPos || isCheckout,
      publicSober: isPublic,
      posSafe: isPos || isCheckout,
      allowAtmosphereAssets: true,
      allowHeavyBlur: !(isTablet || isMobile || isPos || isCheckout || isPublic),
      allowWebgl: false,
      allowPixi: false,
      allowDarkStorm: !(isTablet || isMobile || isPos || isCheckout || isPublic)
    }
  };
}

export function validateRecipeForRoute(recipe = {}, routeBudget = {}) {
  const text = JSON.stringify(recipe).toLowerCase();
  const failures = [];

  if (routeBudget && routeBudget.budget && routeBudget.budget.posSafe) {
    for (const token of ["storm-cloud-operations-real", "obsidian-cloud-motion", "webgl", "pixi"]) {
      if (text.includes(token)) failures.push(`POS-safe route cannot actively use token: ${token}`);
    }
  }

  return {
    ok: failures.length === 0,
    failures,
    warnings: [],
    adapterVersion: ADAPTER_VERSION
  };
}
