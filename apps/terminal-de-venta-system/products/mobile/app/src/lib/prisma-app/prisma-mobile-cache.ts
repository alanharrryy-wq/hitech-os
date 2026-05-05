import { PrismaMobileClientSnapshotSchema, type PrismaMobileClientSnapshot, type PrismaMobileSnapshotPayload } from "./prisma-mobile-snapshot-contract";

const PRISMA_MOBILE_CACHE_KEY = "prisma.mobile.snapshot.v18";
const MAX_CACHE_AGE_MS = 1000 * 60 * 30;

type CachedSnapshotRecord = {
  snapshot: PrismaMobileSnapshotPayload;
  source: "local-cache";
  fetchedAt: string;
  stale: boolean;
  errors: string[];
};

export function readCachedPrismaMobileSnapshot(): PrismaMobileClientSnapshot | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(PRISMA_MOBILE_CACHE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as CachedSnapshotRecord;
    const fetchedAt = Date.parse(parsed.fetchedAt);
    const isExpired = Number.isNaN(fetchedAt) || Date.now() - fetchedAt > MAX_CACHE_AGE_MS;
    return PrismaMobileClientSnapshotSchema.parse({
      ...parsed,
      source: "local-cache",
      stale: true,
      errors: isExpired ? ["La copia local existe, pero ya no está fresca."] : []
    });
  } catch {
    window.localStorage.removeItem(PRISMA_MOBILE_CACHE_KEY);
    return null;
  }
}

export function writeCachedPrismaMobileSnapshot(snapshot: PrismaMobileSnapshotPayload): void {
  if (typeof window === "undefined") return;
  const record: CachedSnapshotRecord = { snapshot, source: "local-cache", fetchedAt: new Date().toISOString(), stale: true, errors: [] };
  try { window.localStorage.setItem(PRISMA_MOBILE_CACHE_KEY, JSON.stringify(record)); } catch {}
}

export function clearCachedPrismaMobileSnapshot(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(PRISMA_MOBILE_CACHE_KEY);
}
