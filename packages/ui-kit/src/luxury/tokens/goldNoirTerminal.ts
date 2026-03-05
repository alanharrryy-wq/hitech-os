import type { LuxuryTokenPack } from "./types.js";
import { buildTokenPackFromCatalog } from "./tokenCatalog.js";

export const GOLD_NOIR_TERMINAL_MANIFEST: readonly string[] = Object.freeze([
  "matte-black-ramp",
  "enamel-gold-hairline",
  "executive-terminal",
  "deal-room-composure",
  "micro-emphasis-only",
  "low-glow-discipline",
  "no-rainbow",
  "no-gamer-led",
  "risk-ledger-aesthetic"
]);

export const goldNoirTerminalTokens: LuxuryTokenPack = buildTokenPackFromCatalog("GOLD_NOIR_TERMINAL");
