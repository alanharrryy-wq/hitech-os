import { isLayerId, sortLayerIds, type LayerId } from "@hitech/ui-kit";
import {
  SCENE_DEFAULT_VIEWPORT_DIMENSIONS,
  SCENE_SCHEMA_VERSION,
  type SceneLayersMode,
  type SceneMotionValue,
  type SceneViewportPreset
} from "./scene-constants";
import { ensureSceneId } from "./scene-id";
import {
  SCENE_SCHEMA_V1,
  SCENE_SCHEMA_V2,
  coerceViewportPreset,
  normalizeSceneInput,
  type LegacySceneRecord,
  type SceneRecord,
  type SceneRecordInput
} from "./scene-schema";

export interface SceneMigrationResult {
  readonly scene: SceneRecord;
  readonly migrated: boolean;
  readonly fromVersion: number;
}

function asIso(value: string | undefined, fallback: string): string {
  if (!value) {
    return fallback;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return fallback;
  }

  return parsed.toISOString();
}

function migrateLegacyLayers(layers: LegacySceneRecord["layers"]): {
  readonly mode: SceneLayersMode;
  readonly layerIds: readonly LayerId[];
} {
  if (!layers || layers === "none") {
    return {
      mode: "none",
      layerIds: []
    };
  }

  if (layers === "all") {
    return {
      mode: "all",
      layerIds: []
    };
  }

  const ids = sortLayerIds(
    Array.from(
      new Set(
        layers
          .map((value) => value.trim())
          .filter((value): value is LayerId => isLayerId(value))
      )
    )
  );

  return {
    mode: ids.length > 0 ? "list" : "none",
    layerIds: ids
  };
}

function migrateLegacyViewport(legacy: LegacySceneRecord): {
  readonly preset: SceneViewportPreset;
  readonly width?: number;
  readonly height?: number;
} {
  const preset = coerceViewportPreset(legacy.viewport);
  if (preset === "custom") {
    return {
      preset,
      width: legacy.customViewport?.width ?? SCENE_DEFAULT_VIEWPORT_DIMENSIONS.desktop.width,
      height: legacy.customViewport?.height ?? SCENE_DEFAULT_VIEWPORT_DIMENSIONS.desktop.height
    };
  }

  return {
    preset
  };
}

function migrateV1ToV2(input: LegacySceneRecord): SceneRecordInput {
  const now = new Date().toISOString();
  const migratedLayers = migrateLegacyLayers(input.layers);
  const route = input.route.startsWith("/") ? input.route : `/${input.route}`;

  const queryParams = new URLSearchParams(input.query ?? "");

  if (migratedLayers.mode === "all") {
    queryParams.set("layers", "all");
  } else if (migratedLayers.mode === "none") {
    queryParams.set("layers", "none");
  } else {
    queryParams.set("layers", migratedLayers.layerIds.join(","));
  }

  queryParams.set("motion", (input.motion ?? "off") as SceneMotionValue);
  queryParams.set("layerProfile", input.layerProfile ?? "neutral");

  return {
    schemaVersion: SCENE_SCHEMA_VERSION,
    id: ensureSceneId(input.id),
    title: input.title,
    route,
    query: queryParams.toString(),
    viewport: migrateLegacyViewport(input),
    layerProfile: input.layerProfile ?? "neutral",
    layers: {
      mode: migratedLayers.mode,
      layerIds: [...migratedLayers.layerIds]
    },
    motion: input.motion ?? "off",
    notes: input.notes,
    tags:
      input.tags
        ?.map((value) => value.trim().toLowerCase().replace(/\s+/g, "-"))
        .filter((value) => value.length > 0) ?? [],
    createdAt: asIso(input.createdAt, now),
    updatedAt: asIso(input.updatedAt, now)
  };
}

export function migrateScene(input: unknown): SceneMigrationResult {
  const parsedV2 = SCENE_SCHEMA_V2.safeParse(input);
  if (parsedV2.success) {
    return {
      scene: parsedV2.data,
      migrated: false,
      fromVersion: SCENE_SCHEMA_VERSION
    };
  }

  const parsedV1 = SCENE_SCHEMA_V1.safeParse(input);
  if (!parsedV1.success) {
    const firstError = parsedV1.error.issues[0]?.message ?? "Unknown scene schema error";
    throw new Error(`Scene migration failed: ${firstError}`);
  }

  const migratedInput = normalizeSceneInput(migrateV1ToV2(parsedV1.data));
  const scene = SCENE_SCHEMA_V2.parse(migratedInput);

  return {
    scene,
    migrated: true,
    fromVersion: 1
  };
}

export function migrateScenes(input: readonly unknown[]): {
  readonly scenes: readonly SceneRecord[];
  readonly migratedCount: number;
} {
  let migratedCount = 0;
  const scenes = input.map((entry) => {
    const result = migrateScene(entry);
    if (result.migrated) {
      migratedCount += 1;
    }
    return result.scene;
  });

  return {
    scenes,
    migratedCount
  };
}
