const SAFE_SCENE_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function normalizeSceneId(input: string): string {
  const normalized = input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "");

  return normalized.length > 0 ? normalized : "scene";
}

export function isSafeSceneId(input: string): boolean {
  return SAFE_SCENE_ID.test(input);
}

export function ensureSceneId(input: string): string {
  const normalized = normalizeSceneId(input);
  return normalized.length > 0 ? normalized : "scene";
}

export function createDuplicateSceneId(baseId: string, existing: ReadonlySet<string>): string {
  const normalizedBase = ensureSceneId(baseId);
  if (!existing.has(normalizedBase)) {
    return normalizedBase;
  }

  let counter = 2;
  while (existing.has(`${normalizedBase}-${counter}`)) {
    counter += 1;
  }

  return `${normalizedBase}-${counter}`;
}
