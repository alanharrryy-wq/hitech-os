import type { LuxuryTokenPack } from "./types.js";
import { buildTokenPackFromCatalog } from "./tokenCatalog.js";

export const LIQUID_GLASS_MANIFEST: readonly string[] = Object.freeze([
  "frosted",
  "specular",
  "pearlescent",
  "translucent-depth",
  "legibility-first",
  "quiet-highlights",
  "apple-vision-material-language",
  "anti-neon",
  "anti-clutter"
]);

export const liquidGlassTokens: LuxuryTokenPack = buildTokenPackFromCatalog("LIQUID_GLASS");
