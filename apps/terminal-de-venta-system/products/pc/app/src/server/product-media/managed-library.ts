/* PRISMA_DARK_PACKSHOTS_197 */
import fs from "node:fs";
import path from "node:path";

export type ManagedPackshotAsset = {
  assetId: string;
  canonicalName: string;
  displayName: string;
  category: string;
  keywords: string[];
  runtimePath: string;
  thumbnailPath: string;
  selectable?: boolean;
};

type ManagedPackshotCatalog = {
  schemaVersion: string;
  libraryId: string;
  mode: "dark_only";
  counts: Record<string, number>;
  items: ManagedPackshotAsset[];
};

function candidateRoots() {
  const configured = process.env.PRISMA_PRODUCT_MEDIA_ROOT?.trim();
  const cwd = process.cwd();
  return [
    configured,
    path.join(cwd, "tools", "_local", "data", "terminal-de-venta-system", "product-media"),
    path.resolve(cwd, "..", "..", "..", "..", "..", "tools", "_local", "data", "terminal-de-venta-system", "product-media"),
    path.resolve(cwd, "..", "..", "..", "..", "tools", "_local", "data", "terminal-de-venta-system", "product-media")
  ].filter((value): value is string => Boolean(value));
}

export function resolveManagedProductMediaRoot() {
  for (const root of candidateRoots()) {
    const manifest = path.join(root, "manifest", "PACKSHOT_CATALOG.json");
    if (fs.existsSync(manifest)) return root;
  }
  return candidateRoots()[0];
}

export function loadManagedPackshotCatalog(): ManagedPackshotCatalog {
  const root = resolveManagedProductMediaRoot();
  const manifestPath = path.join(root, "manifest", "PACKSHOT_CATALOG.json");
  const raw = JSON.parse(fs.readFileSync(manifestPath, "utf8")) as ManagedPackshotCatalog;
  const items = Array.isArray(raw.items) ? raw.items.filter((item) => item && item.selectable !== false) : [];
  return { ...raw, items };
}

export function resolveManagedMediaFile(segments: string[]) {
  if (!Array.isArray(segments) || segments.length !== 2) return null;
  const [bucket, filename] = segments;
  if (!["catalog", "thumbnails"].includes(bucket)) return null;
  if (!/^[a-z0-9][a-z0-9_-]*\.png$/i.test(filename)) return null;
  const root = resolveManagedProductMediaRoot();
  const candidate = path.join(root, bucket, filename);
  const expectedParent = path.join(root, bucket);
  if (path.dirname(candidate) !== expectedParent || !fs.existsSync(candidate) || !fs.statSync(candidate).isFile()) return null;
  return candidate;
}
