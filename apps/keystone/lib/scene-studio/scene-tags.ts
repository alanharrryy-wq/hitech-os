import type { SceneRecord } from "./scene-schema";

export interface SceneSearchFilters {
  readonly term?: string;
  readonly tags?: readonly string[];
  readonly route?: string;
}

export interface SceneTagSummary {
  readonly tag: string;
  readonly count: number;
}

export function buildSceneTagIndex(scenes: readonly SceneRecord[]): readonly SceneTagSummary[] {
  const counts = new Map<string, number>();

  for (const scene of scenes) {
    for (const tag of scene.tags) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1);
    }
  }

  return [...counts.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((left, right) => {
      if (left.count === right.count) {
        return left.tag.localeCompare(right.tag);
      }

      return right.count - left.count;
    });
}

function normalizeTerm(term: string | undefined): string {
  if (!term) {
    return "";
  }

  return term.trim().toLowerCase();
}

export function searchScenes(
  scenes: readonly SceneRecord[],
  filters: SceneSearchFilters
): readonly SceneRecord[] {
  const normalizedTerm = normalizeTerm(filters.term);
  const normalizedTags = new Set((filters.tags ?? []).map((tag) => tag.trim().toLowerCase()));
  const route = filters.route?.trim();

  return scenes.filter((scene) => {
    if (route && scene.route !== route) {
      return false;
    }

    if (normalizedTags.size > 0) {
      const sceneTags = new Set(scene.tags.map((tag) => tag.toLowerCase()));
      for (const tag of normalizedTags) {
        if (!sceneTags.has(tag)) {
          return false;
        }
      }
    }

    if (!normalizedTerm) {
      return true;
    }

    const haystack = [scene.id, scene.title, scene.route, scene.query, ...scene.tags]
      .join(" ")
      .toLowerCase();

    return haystack.includes(normalizedTerm);
  });
}
