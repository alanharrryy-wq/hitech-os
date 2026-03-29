import type { LuxuryTokenPack } from "./types.js";
import { buildTokenPackFromCatalog } from "./tokenCatalog.js";

export const GRAPHITE_PRISM_ISO_MANIFEST: readonly string[] = Object.freeze([
  "graphite-petrol-base",
  "technical-grid-subtle",
  "isometric-showcase",
  "chart-data-prism-only",
  "floating-cards",
  "no-gradient-headlines",
  "no-background-prism",
  "evidence-first-layout",
  "bounded-surface-texture"
]);

export const graphitePrismIsoTokens: LuxuryTokenPack = buildTokenPackFromCatalog("GRAPHITE_PRISM_ISO");
