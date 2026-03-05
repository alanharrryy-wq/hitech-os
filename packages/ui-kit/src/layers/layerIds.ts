export const ALL_LAYERS = [
  "stage.noise",
  "stage.scanlines",
  "stage.glow",
  "stage.haze",
  "stage.vignette",
  "stage.horizon",
  "frame.bezel",
  "card.innerStroke",
  "card.specular",
  "card.grain",
  "card.blur",
  "card.shadowAmbient",
  "inset.shadow",
  "motion.enabled"
] as const;

export type LayerId = (typeof ALL_LAYERS)[number];

export type LayerProfile = "neutral" | "fx" | "perf";

export const CANON_LAYER_IDS = [
  "stage.noise",
  "stage.scanlines",
  "stage.glow",
  "card.innerStroke",
  "card.specular",
  "card.grain",
  "card.blur",
  "motion.enabled",
  "frame.bezel",
  "inset.shadow"
] as const satisfies readonly LayerId[];

export const STAGE_LAYER_IDS = ALL_LAYERS.filter((id) =>
  id.startsWith("stage.")
) as readonly LayerId[];

export const EXPENSIVE_LAYER_IDS = [
  "stage.noise",
  "stage.scanlines",
  "stage.glow",
  "stage.haze",
  "stage.vignette",
  "stage.horizon",
  "card.specular",
  "card.grain",
  "card.blur",
  "card.shadowAmbient"
] as const satisfies readonly LayerId[];

export const PROFILE_PRESETS: Record<LayerProfile, readonly LayerId[]> = {
  neutral: [],
  fx: [...ALL_LAYERS],
  perf: ["card.innerStroke", "frame.bezel", "inset.shadow"]
} as const;

export type LayerFlags = Record<LayerId, boolean>;

export const LAYER_DATA_ATTR_MAP: Readonly<Record<LayerId, string>> = {
  "stage.noise": "data-layer-stage-noise",
  "stage.scanlines": "data-layer-stage-scanlines",
  "stage.glow": "data-layer-stage-glow",
  "stage.haze": "data-layer-stage-haze",
  "stage.vignette": "data-layer-stage-vignette",
  "stage.horizon": "data-layer-stage-horizon",
  "frame.bezel": "data-layer-frame-bezel",
  "card.innerStroke": "data-layer-card-inner-stroke",
  "card.specular": "data-layer-card-specular",
  "card.grain": "data-layer-card-grain",
  "card.blur": "data-layer-card-blur",
  "card.shadowAmbient": "data-layer-card-shadow-ambient",
  "inset.shadow": "data-layer-inset-shadow",
  "motion.enabled": "data-layer-motion"
};

export const LAYER_DATA_ATTRIBUTES = LAYER_DATA_ATTR_MAP;

export const LAYER_SET: ReadonlySet<LayerId> = new Set(ALL_LAYERS);

function createFlags(initialValue: boolean): LayerFlags {
  const flags = {} as LayerFlags;
  for (const id of ALL_LAYERS) {
    flags[id] = initialValue;
  }
  return flags;
}

export function createAllLayersOff(): LayerFlags {
  return createFlags(false);
}

export function createAllLayersOn(): LayerFlags {
  return createFlags(true);
}

export const PROFILE_LAYER_FLAGS: Readonly<Record<LayerProfile, LayerFlags>> = {
  neutral: createAllLayersOff(),
  fx: createAllLayersOn(),
  perf: createFlags(false)
};
for (const id of PROFILE_PRESETS.perf) {
  PROFILE_LAYER_FLAGS.perf[id] = true;
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

export function stableSortLayerIds(ids: readonly LayerId[]): LayerId[] {
  return sortLayerIds(ids);
}

export function listEnabledLayers(flags: LayerFlags): LayerId[] {
  return ALL_LAYERS.filter((id) => flags[id]);
}

export function getEnabledLayerIds(flags: LayerFlags): LayerId[] {
  return listEnabledLayers(flags);
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

  const merged = { ...base };
  for (const id of ALL_LAYERS) {
    const override = overrides[id];
    if (override !== undefined) {
      merged[id] = override;
    }
  }
  return merged;
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

  return stableSortLayerIds([...unique]);
}

export function toOnOff(value: boolean): "on" | "off" {
  return value ? "on" : "off";
}
