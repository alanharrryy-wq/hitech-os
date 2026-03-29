export function normalizePathLike(value: unknown): string | null {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  if (value && typeof value === "object") {
    const maybeRecord = value as Record<string, unknown>;
    const providerPath = maybeRecord.ProviderPath;
    if (typeof providerPath === "string" && providerPath.trim().length > 0) {
      return providerPath;
    }
    const path = maybeRecord.Path;
    if (typeof path === "string" && path.trim().length > 0) {
      return path;
    }
    const current = maybeRecord.CurrentFileSystemLocation;
    if (typeof current === "string" && current.trim().length > 0) {
      return current;
    }
  }
  return null;
}
