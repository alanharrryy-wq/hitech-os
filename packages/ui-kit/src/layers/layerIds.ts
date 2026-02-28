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
  "inset.shadow",
] as const;

export type LayerId = (typeof CANON_LAYER_IDS)[number];

export const LAYER_PROFILES = ["neutral", "perf", "fx"] as const;

export type LayerProfileId = (typeof LAYER_PROFILES)[number];

export type LayerFlags = {
  readonly [id in LayerId]: boolean;
};

export type MutableLayerFlags = {
  [id in LayerId]: boolean;
};

export const DEFAULT_LAYER_PROFILE: LayerProfileId = "neutral";

export const EXPENSIVE_LAYER_IDS = [
  "stage.noise",
  "stage.scanlines",
  "stage.glow",
  "card.specular",
  "card.grain",
  "card.blur",
  "motion.enabled",
] as const satisfies readonly LayerId[];

export type ExpensiveLayerId = (typeof EXPENSIVE_LAYER_IDS)[number];

export const LAYER_DATA_ATTR_MAP = {
  "stage.noise": "data-layer-stage-noise",
  "stage.scanlines": "data-layer-stage-scanlines",
  "stage.glow": "data-layer-stage-glow",
  "card.innerStroke": "data-layer-card-inner-stroke",
  "card.specular": "data-layer-card-specular",
  "card.grain": "data-layer-card-grain",
  "card.blur": "data-layer-card-blur",
  "motion.enabled": "data-layer-motion",
  "frame.bezel": "data-layer-frame-bezel",
  "inset.shadow": "data-layer-inset-shadow",
} as const satisfies Record<LayerId, string>;

export type LayerDataAttrName = (typeof LAYER_DATA_ATTR_MAP)[LayerId];

export type LayerDataAttrState = {
  readonly [dataAttr in LayerDataAttrName]?: "on" | "off";
};

export const STAGE_LAYER_IDS = ["stage.noise", "stage.scanlines", "stage.glow", "motion.enabled"] as const satisfies readonly LayerId[];

export const GLASS_CARD_LAYER_IDS = [
  "card.innerStroke",
  "card.specular",
  "card.grain",
  "card.blur",
  "motion.enabled",
  "frame.bezel",
] as const satisfies readonly LayerId[];

export const INSET_PANEL_LAYER_IDS = ["inset.shadow", "frame.bezel", "motion.enabled"] as const satisfies readonly LayerId[];

export const LAYER_ID_SET: ReadonlySet<LayerId> = new Set(CANON_LAYER_IDS);

export function isLayerId(value: string): value is LayerId {
  return (LAYER_ID_SET as Set<string>).has(value);
}

export function isLayerProfileId(value: string): value is LayerProfileId {
  return (LAYER_PROFILES as readonly string[]).includes(value);
}

export function normalizeLayerToken(value: string): string {
  return value.trim().toLowerCase();
}

export function createAllLayersOff(): MutableLayerFlags {
  const flags = {} as MutableLayerFlags;
  for (const id of CANON_LAYER_IDS) {
    flags[id] = false;
  }
  return flags;
}

export function createAllLayersOn(): MutableLayerFlags {
  const flags = {} as MutableLayerFlags;
  for (const id of CANON_LAYER_IDS) {
    flags[id] = true;
  }
  return flags;
}

export function createLayerFlags(enabledIds: Iterable<LayerId>): MutableLayerFlags {
  const flags = createAllLayersOff();
  for (const id of enabledIds) {
    flags[id] = true;
  }
  return flags;
}

export function cloneLayerFlags(flags: LayerFlags): MutableLayerFlags {
  const clone = {} as MutableLayerFlags;
  for (const id of CANON_LAYER_IDS) {
    clone[id] = Boolean(flags[id]);
  }
  return clone;
}

export function toOnOff(value: boolean): "on" | "off" {
  return value ? "on" : "off";
}

export function getEnabledLayerIds(flags: LayerFlags): LayerId[] {
  const enabled: LayerId[] = [];
  for (const id of CANON_LAYER_IDS) {
    if (flags[id]) {
      enabled.push(id);
    }
  }
  return enabled;
}

export function getDisabledLayerIds(flags: LayerFlags): LayerId[] {
  const disabled: LayerId[] = [];
  for (const id of CANON_LAYER_IDS) {
    if (!flags[id]) {
      disabled.push(id);
    }
  }
  return disabled;
}

function sortByCanonicalOrder(ids: readonly LayerId[]): LayerId[] {
  const index = new Map<LayerId, number>();
  for (let i = 0; i < CANON_LAYER_IDS.length; i += 1) {
    index.set(CANON_LAYER_IDS[i], i);
  }
  const sorted = [...ids];
  sorted.sort((a, b) => (index.get(a) ?? Number.MAX_SAFE_INTEGER) - (index.get(b) ?? Number.MAX_SAFE_INTEGER));
  return sorted;
}

const PERF_ENABLED_IDS = sortByCanonicalOrder(["card.innerStroke", "frame.bezel", "inset.shadow"]);

export const PROFILE_LAYER_FLAGS = {
  neutral: createAllLayersOff(),
  perf: createLayerFlags(PERF_ENABLED_IDS),
  fx: createAllLayersOn(),
} as const satisfies Record<LayerProfileId, LayerFlags>;

export function buildDataAttrStateForFlags(flags: LayerFlags, ids: readonly LayerId[] = CANON_LAYER_IDS): LayerDataAttrState {
  const output: Record<string, "on" | "off"> = {};
  for (const id of ids) {
    output[LAYER_DATA_ATTR_MAP[id]] = toOnOff(Boolean(flags[id]));
  }
  return output as LayerDataAttrState;
}

export function getProfileLayerFlags(profile: LayerProfileId): MutableLayerFlags {
  return cloneLayerFlags(PROFILE_LAYER_FLAGS[profile]);
}

export function stableSortLayerIds(ids: readonly LayerId[]): LayerId[] {
  return sortByCanonicalOrder(ids);
}

export function areFlagsEqual(left: LayerFlags, right: LayerFlags): boolean {
  for (const id of CANON_LAYER_IDS) {
    if (Boolean(left[id]) !== Boolean(right[id])) {
      return false;
    }
  }
  return true;
}

export function countEnabledFlags(flags: LayerFlags): number {
  let count = 0;
  for (const id of CANON_LAYER_IDS) {
    if (flags[id]) {
      count += 1;
    }
  }
  return count;
}
