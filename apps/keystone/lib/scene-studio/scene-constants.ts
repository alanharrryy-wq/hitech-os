import { ALL_LAYERS, type LayerId, type LayerProfile } from "@hitech/ui-kit";

export const SCENE_STUDIO_ROUTE = "/dev/scene-studio";
export const SCENE_STUDIO_STORAGE_KEY = "keystone.sceneStudio.scenes.v2";
export const SCENE_STUDIO_SCHEMA_VERSION = 2 as const;
export const SCENE_SCHEMA_VERSION = SCENE_STUDIO_SCHEMA_VERSION;

export const SCENE_VIEWPORT_PRESETS = ["desktop", "mobile", "tablet", "custom"] as const;
export type SceneViewportPreset = (typeof SCENE_VIEWPORT_PRESETS)[number];

export const SCENE_MOTION_VALUES = ["on", "off"] as const;
export type SceneMotionValue = (typeof SCENE_MOTION_VALUES)[number];

export const SCENE_LAYER_PROFILE_VALUES = ["neutral", "fx", "perf"] as const satisfies readonly LayerProfile[];
export type SceneLayerProfile = (typeof SCENE_LAYER_PROFILE_VALUES)[number];

export const SCENE_LAYERS_MODE_VALUES = ["none", "all", "list"] as const;
export type SceneLayersMode = (typeof SCENE_LAYERS_MODE_VALUES)[number];

export const SCENE_QUERY_PRIORITY_KEYS = ["layers", "layerProfile", "motion", "debug", "viewport"] as const;

export const SCENE_DEFAULT_VIEWPORT_DIMENSIONS: Readonly<Record<Exclude<SceneViewportPreset, "custom">, { width: number; height: number }>> = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
  tablet: { width: 1024, height: 1366 }
};

export const SCENE_CANONICAL_LAYER_IDS: readonly LayerId[] = ALL_LAYERS;
