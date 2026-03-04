import type { LayerId } from "@hitech/ui-kit";
import { SCENE_SCHEMA_VERSION } from "./scene-constants";
import { SCENE_SCHEMA_V2, type SceneRecord } from "./scene-schema";

interface DefaultSceneSeed {
  readonly id: string;
  readonly title: string;
  readonly route: string;
  readonly query: string;
  readonly viewport: SceneRecord["viewport"];
  readonly layerProfile: SceneRecord["layerProfile"];
  readonly layers: SceneRecord["layers"];
  readonly motion: SceneRecord["motion"];
  readonly tags: string[];
  readonly notes?: string;
}

function emptyList(): LayerId[] {
  return [];
}

const DEFAULT_SCENE_SEEDS: DefaultSceneSeed[] = [
  {
    id: "pitch-01-double-engine-neutral-desktop",
    title: "Pitch 01 Neutral Desktop",
    route: "/pitch/01-double-engine",
    query: "debug=1&layers=none&layerProfile=neutral&motion=off",
    viewport: { preset: "desktop" },
    layerProfile: "neutral",
    layers: { mode: "none", layerIds: emptyList() },
    motion: "off",
    tags: ["pitch", "01", "neutral", "desktop"]
  },
  {
    id: "pitch-01-double-engine-fx-desktop",
    title: "Pitch 01 FX Desktop",
    route: "/pitch/01-double-engine",
    query: "debug=1&layerProfile=fx&layers=all&motion=on",
    viewport: { preset: "desktop" },
    layerProfile: "fx",
    layers: { mode: "all", layerIds: emptyList() },
    motion: "on",
    tags: ["pitch", "01", "fx", "desktop"]
  },
  {
    id: "pitch-02-industrial-flow-neutral-desktop",
    title: "Pitch 02 Neutral Desktop",
    route: "/pitch/02-industrial-flow",
    query: "debug=1&layers=none&layerProfile=neutral&motion=off",
    viewport: { preset: "desktop" },
    layerProfile: "neutral",
    layers: { mode: "none", layerIds: emptyList() },
    motion: "off",
    tags: ["pitch", "02", "neutral", "desktop"]
  },
  {
    id: "pitch-02-industrial-flow-layered-desktop",
    title: "Pitch 02 Layered Desktop",
    route: "/pitch/02-industrial-flow",
    query: "debug=1&layers=stage.haze,stage.vignette,card.specular&layerProfile=neutral&motion=off",
    viewport: { preset: "desktop" },
    layerProfile: "neutral",
    layers: {
      mode: "list",
      layerIds: ["stage.haze", "stage.vignette", "card.specular"]
    },
    motion: "off",
    tags: ["pitch", "02", "layered", "desktop"],
    notes: "Core layer override regression scene"
  },
  {
    id: "pitch-03-hitech-os-fx-desktop",
    title: "Pitch 03 FX Desktop",
    route: "/pitch/03-hitech-os",
    query: "debug=1&layerProfile=fx&layers=all&motion=on",
    viewport: { preset: "desktop" },
    layerProfile: "fx",
    layers: { mode: "all", layerIds: emptyList() },
    motion: "on",
    tags: ["pitch", "03", "fx", "desktop"]
  },
  {
    id: "pitch-03-hitech-os-perf-mobile",
    title: "Pitch 03 Perf Mobile",
    route: "/pitch/03-hitech-os",
    query: "debug=1&layerProfile=perf&layers=none&motion=off",
    viewport: { preset: "mobile" },
    layerProfile: "perf",
    layers: { mode: "none", layerIds: emptyList() },
    motion: "off",
    tags: ["pitch", "03", "perf", "mobile"]
  },
  {
    id: "pitch-04-valuation-perf-mobile",
    title: "Pitch 04 Perf Mobile",
    route: "/pitch/04-valuation",
    query: "debug=1&layerProfile=perf&layers=none&motion=off",
    viewport: { preset: "mobile" },
    layerProfile: "perf",
    layers: { mode: "none", layerIds: emptyList() },
    motion: "off",
    tags: ["pitch", "04", "perf", "mobile"]
  },
  {
    id: "pitch-04-valuation-fx-tablet",
    title: "Pitch 04 FX Tablet",
    route: "/pitch/04-valuation",
    query: "debug=1&layerProfile=fx&layers=all&motion=on",
    viewport: { preset: "tablet" },
    layerProfile: "fx",
    layers: { mode: "all", layerIds: emptyList() },
    motion: "on",
    tags: ["pitch", "04", "fx", "tablet"]
  }
];

export function createDefaultSceneLibrary(timestamp = new Date().toISOString()): readonly SceneRecord[] {
  return DEFAULT_SCENE_SEEDS.map((seed) =>
    SCENE_SCHEMA_V2.parse({
      schemaVersion: SCENE_SCHEMA_VERSION,
      ...seed,
      createdAt: timestamp,
      updatedAt: timestamp
    })
  );
}

export const KNOWN_PITCH_ROUTES = [
  "/pitch",
  "/pitch/01-double-engine",
  "/pitch/02-industrial-flow",
  "/pitch/03-hitech-os",
  "/pitch/04-valuation",
  "/pitch/05-inventory-foundation",
  "/pitch/06-shipments-receiving"
] as const;
