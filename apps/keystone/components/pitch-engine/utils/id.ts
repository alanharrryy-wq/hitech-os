export function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "")
    .slice(0, 64);
}

export function nowIso(): string {
  return new Date().toISOString();
}

export function ensureUniqueId(baseId: string, existingIds: readonly string[]): string {
  if (!existingIds.includes(baseId)) {
    return baseId;
  }

  let suffix = 2;
  while (existingIds.includes(`${baseId}-${suffix}`)) {
    suffix += 1;
  }

  return `${baseId}-${suffix}`;
}

export function buildStableId(prefix: string, name: string, existingIds: readonly string[]): string {
  const normalized = slugify(name);
  const base = normalized.length > 0 ? `${prefix}-${normalized}` : `${prefix}-item`;
  return ensureUniqueId(base, existingIds);
}
