export const prismaChartStateGallery = {
  happy: "Data is present, fresh, and high-confidence.",
  empty: "No records exist for the selected scope; do not render fake marks.",
  partial: "Some safe sources are present but coverage is incomplete.",
  stale: "A source is older than its accepted freshness window.",
  offline: "A source is unreachable; chart must explain missing coverage.",
  unknown: "The adapter cannot determine state safely.",
  dense: "The chart has many records and should reduce labels before reducing truth.",
  critical: "Evidence-backed severity only; no high/critical visual state without evidence."
} as const;

export type PrismaChartStateName = keyof typeof prismaChartStateGallery;

