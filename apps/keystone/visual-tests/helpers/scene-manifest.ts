import { readFile } from "node:fs/promises";
import { SCENES_MANIFEST_PATH } from "./paths.js";

export type SceneViewport = "desktop" | "mobile" | "tablet" | "custom";

export interface SceneManifestEntry {
  readonly route: string;
  readonly query?: string;
  readonly viewport: SceneViewport;
  readonly viewportWidth?: number;
  readonly viewportHeight?: number;
  readonly title?: string;
  readonly tags?: readonly string[];
  readonly notes?: string;
}

export interface VisualSceneDefinition extends SceneManifestEntry {
  readonly id: string;
  readonly canonicalQuery: string;
}

const SCENE_QUERY_ORDER = ["layers", "layerProfile", "motion", "debug"] as const;

function canonicalizeQuery(rawQuery?: string): string {
  const params = new URLSearchParams(rawQuery ?? "");
  const canonical = new URLSearchParams();
  const used = new Set<string>();

  for (const key of SCENE_QUERY_ORDER) {
    used.add(key);
    for (const value of params.getAll(key)) {
      canonical.append(key, value);
    }
  }

  const remainingKeys = [...new Set(params.keys())]
    .filter((key) => !used.has(key))
    .sort((left, right) => left.localeCompare(right));

  for (const key of remainingKeys) {
    for (const value of params.getAll(key)) {
      canonical.append(key, value);
    }
  }

  return canonical.toString().replaceAll("%2C", ",");
}

function normalizeScene(id: string, entry: SceneManifestEntry): VisualSceneDefinition {
  if (!entry.route.startsWith("/")) {
    throw new Error(`Scene "${id}" route must start with '/'. Received "${entry.route}".`);
  }

  if (!["desktop", "mobile", "tablet", "custom"].includes(entry.viewport)) {
    throw new Error(
      `Scene "${id}" viewport must be desktop|mobile|tablet|custom. Received "${entry.viewport}".`
    );
  }

  if (entry.viewport === "custom") {
    if (!entry.viewportWidth || !entry.viewportHeight) {
      throw new Error(
        `Scene "${id}" uses custom viewport but viewportWidth/viewportHeight were not provided.`
      );
    }
  }

  return {
    id,
    route: entry.route,
    viewport: entry.viewport,
    ...(entry.query !== undefined ? { query: entry.query } : {}),
    ...(entry.viewportWidth ? { viewportWidth: entry.viewportWidth } : {}),
    ...(entry.viewportHeight ? { viewportHeight: entry.viewportHeight } : {}),
    ...(entry.title ? { title: entry.title } : {}),
    ...(entry.tags ? { tags: entry.tags } : {}),
    ...(entry.notes ? { notes: entry.notes } : {}),
    canonicalQuery: canonicalizeQuery(entry.query)
  };
}

export function buildScenePath(scene: VisualSceneDefinition): string {
  if (!scene.canonicalQuery) {
    return scene.route;
  }

  return `${scene.route}?${scene.canonicalQuery}`;
}

export function parseSceneLayerParams(scene: VisualSceneDefinition): {
  readonly layers: string;
  readonly layerProfile: string;
  readonly motion: string;
} {
  const search = new URLSearchParams(scene.canonicalQuery);

  return {
    layers: search.get("layers") ?? "",
    layerProfile: search.get("layerProfile") ?? "",
    motion: search.get("motion") ?? ""
  };
}

export interface SceneManifestFilters {
  readonly ids?: readonly string[];
  readonly route?: string;
  readonly tags?: readonly string[];
  readonly smoke?: boolean;
}

export function filterSceneManifest(
  scenes: readonly VisualSceneDefinition[],
  filters: SceneManifestFilters
): readonly VisualSceneDefinition[] {
  const allowedIds = filters.ids ? new Set(filters.ids) : null;
  const tagSet = filters.tags ? new Set(filters.tags.map((tag) => tag.toLowerCase())) : null;

  return scenes.filter((scene, index) => {
    if (allowedIds && !allowedIds.has(scene.id)) {
      return false;
    }

    if (filters.route && scene.route !== filters.route) {
      return false;
    }

    if (tagSet) {
      const sceneTags = new Set((scene.tags ?? []).map((tag) => tag.toLowerCase()));
      for (const tag of tagSet) {
        if (!sceneTags.has(tag)) {
          return false;
        }
      }
    }

    if (filters.smoke) {
      return index < 3 || (scene.tags ?? []).includes("smoke");
    }

    return true;
  });
}

export async function loadSceneManifest(): Promise<readonly VisualSceneDefinition[]> {
  const raw = await readFile(SCENES_MANIFEST_PATH, "utf8");
  const parsed = JSON.parse(raw) as Record<string, SceneManifestEntry>;

  return Object.entries(parsed)
    .map(([id, entry]) => normalizeScene(id, entry))
    .sort((left, right) => left.id.localeCompare(right.id));
}
