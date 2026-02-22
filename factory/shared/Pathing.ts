const WINDOWS_ABSOLUTE_PATTERN = /^[a-zA-Z]:[\\/]/;
const UNC_PATH_PATTERN = /^\\\\/;
const SAFE_REPO_PATH_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+$/;

export function normalizeRepoPath(pathLike: string): string {
  const normalized = pathLike.replace(/\\/g, "/").trim();
  return normalized.replace(/\/+/g, "/");
}

export function isRepoRelativePath(pathLike: string): boolean {
  if (pathLike.length === 0) {
    return false;
  }

  const normalized = normalizeRepoPath(pathLike);
  if (normalized.startsWith("/")) {
    return false;
  }
  if (normalized.includes("..")) {
    return false;
  }
  if (WINDOWS_ABSOLUTE_PATTERN.test(pathLike) || UNC_PATH_PATTERN.test(pathLike)) {
    return false;
  }
  return SAFE_REPO_PATH_PATTERN.test(normalized);
}

export function assertRepoRelativePath(pathLike: string, contextLabel: string): string {
  if (!isRepoRelativePath(pathLike)) {
    throw new Error(`${contextLabel} must be a repo-relative safe path: ${pathLike}`);
  }
  return normalizeRepoPath(pathLike);
}

export function compareRepoPaths(left: string, right: string): number {
  const normalizedLeft = normalizeRepoPath(left);
  const normalizedRight = normalizeRepoPath(right);
  return normalizedLeft.localeCompare(normalizedRight);
}
