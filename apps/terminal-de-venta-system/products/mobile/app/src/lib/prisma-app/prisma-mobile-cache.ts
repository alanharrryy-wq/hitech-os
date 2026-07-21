import type {
  PrismaMobileClientSnapshot,
  PrismaMobileSnapshotPayload
} from "./prisma-mobile-snapshot-contract";

const LEGACY_PRISMA_MOBILE_CACHE_KEY = "prisma.mobile.snapshot.v18";
const MAX_MEMORY_CACHE_AGE_MS = 1000 * 60 * 5;

let memorySnapshot: PrismaMobileClientSnapshot | null = null;

function purgeLegacyPersistentSnapshot(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(LEGACY_PRISMA_MOBILE_CACHE_KEY);
  } catch {
    // Storage can be unavailable in hardened browsers. The cache remains memory-only.
  }
}

export function readCachedPrismaMobileSnapshot(): PrismaMobileClientSnapshot | null {
  purgeLegacyPersistentSnapshot();
  if (!memorySnapshot) return null;

  const fetchedAt = Date.parse(memorySnapshot.fetchedAt);
  const expired =
    Number.isNaN(fetchedAt) ||
    Date.now() - fetchedAt > MAX_MEMORY_CACHE_AGE_MS;

  if (expired) {
    memorySnapshot = null;
    return null;
  }

  return {
    ...memorySnapshot,
    source: "local-cache",
    stale: true,
    errors: ["Lectura temporal en memoria; solicita datos frescos."]
  };
}

export function writeCachedPrismaMobileSnapshot(snapshot: PrismaMobileSnapshotPayload): void {
  purgeLegacyPersistentSnapshot();
  memorySnapshot = {
    snapshot,
    source: "local-cache",
    fetchedAt: new Date().toISOString(),
    stale: true,
    errors: []
  };
}

export function clearCachedPrismaMobileSnapshot(): void {
  memorySnapshot = null;
  purgeLegacyPersistentSnapshot();
}
