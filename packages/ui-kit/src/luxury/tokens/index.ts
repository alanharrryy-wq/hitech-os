import type { StyleId } from "../types.js";
import type { LuxuryTokenPack } from "./types.js";
import { goldNoirTerminalTokens } from "./goldNoirTerminal.js";
import { graphitePrismIsoTokens } from "./graphitePrismIso.js";
import { liquidGlassTokens } from "./liquidGlass.js";
export { buildTokenPackFromCatalog } from "./tokenCatalog.js";

export { liquidGlassTokens } from "./liquidGlass.js";
export { goldNoirTerminalTokens } from "./goldNoirTerminal.js";
export { graphitePrismIsoTokens } from "./graphitePrismIso.js";
export type {
  ElevationLevel,
  ElevationRamp,
  ElevationToken,
  GlowBudget,
  GoldUsagePolicy,
  LuxuryPolicyBudgets,
  LuxuryTokenPack,
  MotionBudget,
  NeutralRamp,
  SemanticAccent,
  SemanticAccentRamp,
  StrokeRamp,
  TexturePolicy
} from "./types.js";

export const LUXURY_TOKEN_PACKS: Readonly<Record<StyleId, LuxuryTokenPack>> = Object.freeze({
  LIQUID_GLASS: liquidGlassTokens,
  GOLD_NOIR_TERMINAL: goldNoirTerminalTokens,
  GRAPHITE_PRISM_ISO: graphitePrismIsoTokens
});

export function getLuxuryTokens(styleId: StyleId): LuxuryTokenPack {
  return LUXURY_TOKEN_PACKS[styleId];
}
