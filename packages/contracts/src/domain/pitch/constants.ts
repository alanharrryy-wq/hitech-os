export const PITCH_DECK_ID = "hitech-pitch-terraform-v1" as const;
export const PITCH_DECK_VERSION = "1.0.0" as const;
export const PITCH_LOCALE = "es-MX" as const;

export const PITCH_SCREEN_SLUGS = [
  "01-double-engine",
  "02-industrial-flow",
  "03-hitech-os",
  "04-valuation"
] as const;

export type PitchScreenSlug = (typeof PITCH_SCREEN_SLUGS)[number];

export const PITCH_ROUTE_BASE = "/pitch" as const;

export const PITCH_ROUTES: Readonly<
  Record<PitchScreenSlug, `${typeof PITCH_ROUTE_BASE}/${PitchScreenSlug}`>
> = {
  "01-double-engine": "/pitch/01-double-engine",
  "02-industrial-flow": "/pitch/02-industrial-flow",
  "03-hitech-os": "/pitch/03-hitech-os",
  "04-valuation": "/pitch/04-valuation"
};

export const PITCH_SCREEN_ORDER: readonly PitchScreenSlug[] = PITCH_SCREEN_SLUGS;

export const PITCH_LAYER_PROFILE_HINTS = ["neutral", "fx", "perf"] as const;
export type PitchLayerProfileHint = (typeof PITCH_LAYER_PROFILE_HINTS)[number];

export const PITCH_COPY_LOCK_NOTICE =
  "Canonical copy is contract-locked. Do not mutate strings outside contract fixtures." as const;

export const PITCH_SCREEN_TITLES: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine": "HITECH — ARQUITECTURA DE DOBLE MOTOR",
  "02-industrial-flow": "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE",
  "03-hitech-os": "MOTOR 2 — HITECH OS (Infraestructura Digital)",
  "04-valuation": "ESTRUCTURA FINANCIERA + VALUACIÓN"
};

export const PITCH_ANCHORS: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine": "double-engine",
  "02-industrial-flow": "industrial-flow",
  "03-hitech-os": "hitech-os",
  "04-valuation": "valuation"
};

export const PITCH_SCREEN_NUMBERS: Readonly<Record<PitchScreenSlug, 1 | 2 | 3 | 4>> = {
  "01-double-engine": 1,
  "02-industrial-flow": 2,
  "03-hitech-os": 3,
  "04-valuation": 4
};

export const PITCH_TABLE_HEADERS = ["Modelo", "Múltiplo", "Riesgo", "Escalabilidad"] as const;

export const PITCH_COMPARISON_ROWS = [
  ["Industrial tradicional", "Bajo", "Medio", "Limitada"],
  ["Industrial + Software", "Alto", "Controlado", "Alta"]
] as const;

export const PITCH_VALIDATION_MESSAGES = {
  missingScreen: "Pitch screen fixture is missing.",
  duplicatedSlug: "Pitch deck has duplicated screen slugs.",
  invalidOrder: "Pitch deck screen order is not canonical.",
  routeMismatch: "Pitch route table does not match canonical route list."
} as const;

export const PITCH_SCHEMA_TAGS = {
  deck: "pitch.deck",
  screen: "pitch.screen",
  screen01: "pitch.screen.01",
  screen02: "pitch.screen.02",
  screen03: "pitch.screen.03",
  screen04: "pitch.screen.04"
} as const;
