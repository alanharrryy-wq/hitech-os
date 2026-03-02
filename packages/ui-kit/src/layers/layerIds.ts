export const ALL_LAYERS = [
  "stage.haze",
  "stage.vignette",
  "stage.noise",
  "stage.scanlines",
  "stage.horizon",
  "frame.bezel",
  "card.blur",
  "card.innerStroke",
  "card.specular",
  "card.grain",
  "card.shadowAmbient",
  "inset.shadow",
  "motion.enabled"
] as const;

export type LayerId = (typeof ALL_LAYERS)[number];

export type LayerProfile = "neutral" | "fx" | "perf";

export const PROFILE_PRESETS: Record<LayerProfile, readonly LayerId[]> = {
  neutral: [],
  fx: [
    "stage.haze",
    "stage.vignette",
    "stage.noise",
    "stage.scanlines",
    "stage.horizon",
    "frame.bezel",
    "card.innerStroke",
    "card.shadowAmbient",
    "card.specular",
    "card.grain",
    "inset.shadow"
  ],
  perf: ["stage.vignette", "card.innerStroke", "inset.shadow"]
} as const;

export const LAYER_SET: ReadonlySet<LayerId> = new Set(ALL_LAYERS);

export type LayerFlags = Record<LayerId, boolean>;

export const LAYER_DATA_ATTRIBUTES: Readonly<Record<LayerId, string>> = {
  "stage.haze": "data-layer-stage-haze",
  "stage.vignette": "data-layer-stage-vignette",
  "stage.noise": "data-layer-stage-noise",
  "stage.scanlines": "data-layer-stage-scanlines",
  "stage.horizon": "data-layer-stage-horizon",
  "frame.bezel": "data-layer-frame-bezel",
  "card.blur": "data-layer-card-blur",
  "card.innerStroke": "data-layer-card-inner-stroke",
  "card.specular": "data-layer-card-specular",
  "card.grain": "data-layer-card-grain",
  "card.shadowAmbient": "data-layer-card-shadow-ambient",
  "inset.shadow": "data-layer-inset-shadow",
  "motion.enabled": "data-layer-motion-enabled"
};

export function createAllLayersOff(): LayerFlags {
  return {
    "stage.haze": false,
    "stage.vignette": false,
    "stage.noise": false,
    "stage.scanlines": false,
    "stage.horizon": false,
    "frame.bezel": false,
    "card.blur": false,
    "card.innerStroke": false,
    "card.specular": false,
    "card.grain": false,
    "card.shadowAmbient": false,
    "inset.shadow": false,
    "motion.enabled": false
  };
}

export function createAllLayersOn(): LayerFlags {
  return {
    "stage.haze": true,
    "stage.vignette": true,
    "stage.noise": true,
    "stage.scanlines": true,
    "stage.horizon": true,
    "frame.bezel": true,
    "card.blur": true,
    "card.innerStroke": true,
    "card.specular": true,
    "card.grain": true,
    "card.shadowAmbient": true,
    "inset.shadow": true,
    "motion.enabled": true
  };
}

export function applyLayerPreset(profile: LayerProfile): LayerFlags {
  const flags = createAllLayersOff();
  const enabled = PROFILE_PRESETS[profile] ?? [];
  for (const id of enabled) {
    flags[id] = true;
  }
  return flags;
}

export function isLayerId(value: string): value is LayerId {
  return LAYER_SET.has(value as LayerId);
}

export function sortLayerIds(ids: readonly LayerId[]): LayerId[] {
  return [...ids].sort((left, right) => ALL_LAYERS.indexOf(left) - ALL_LAYERS.indexOf(right));
}

export function listEnabledLayers(flags: LayerFlags): LayerId[] {
  return ALL_LAYERS.filter((id) => flags[id]);
}

export function areAllLayersEnabled(flags: LayerFlags): boolean {
  return ALL_LAYERS.every((id) => flags[id]);
}

export function areAllLayersDisabled(flags: LayerFlags): boolean {
  return ALL_LAYERS.every((id) => !flags[id]);
}

export function mergeLayerFlags(base: LayerFlags, overrides?: Partial<LayerFlags>): LayerFlags {
  if (!overrides) {
    return base;
  }

  return {
    "stage.haze": overrides["stage.haze"] ?? base["stage.haze"],
    "stage.vignette": overrides["stage.vignette"] ?? base["stage.vignette"],
    "stage.noise": overrides["stage.noise"] ?? base["stage.noise"],
    "stage.scanlines": overrides["stage.scanlines"] ?? base["stage.scanlines"],
    "stage.horizon": overrides["stage.horizon"] ?? base["stage.horizon"],
    "frame.bezel": overrides["frame.bezel"] ?? base["frame.bezel"],
    "card.blur": overrides["card.blur"] ?? base["card.blur"],
    "card.innerStroke": overrides["card.innerStroke"] ?? base["card.innerStroke"],
    "card.specular": overrides["card.specular"] ?? base["card.specular"],
    "card.grain": overrides["card.grain"] ?? base["card.grain"],
    "card.shadowAmbient": overrides["card.shadowAmbient"] ?? base["card.shadowAmbient"],
    "inset.shadow": overrides["inset.shadow"] ?? base["inset.shadow"],
    "motion.enabled": overrides["motion.enabled"] ?? base["motion.enabled"]
  };
}

export function createFlagsFromEnabledLayers(enabledLayers: readonly LayerId[]): LayerFlags {
  const flags = createAllLayersOff();
  for (const id of enabledLayers) {
    flags[id] = true;
  }
  return flags;
}

export function parseLayerList(input: string): LayerId[] {
  const entries = input
    .split(",")
    .map((value) => value.trim())
    .filter((value) => value.length > 0);

  const unique = new Set<LayerId>();
  for (const entry of entries) {
    if (isLayerId(entry)) {
      unique.add(entry);
    }
  }

  return sortLayerIds([...unique]);
}
