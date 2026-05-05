import { promises as fs } from "node:fs";
import path from "node:path";

export type LocalCatalogProductInput = {
  id?: string;
  businessId?: string;
  sku: string;
  barcode?: string | null;
  name: string;
  category?: string | null;
  priceCents: number;
  stockOnHand?: number;
  lowStockThreshold?: number;
  isActive?: boolean;
  updatedAt?: string;
};

export type LocalCatalogProduct = Required<Omit<LocalCatalogProductInput, "barcode" | "category">> & {
  barcode: string | null;
  category: string | null;
};

type LocalCatalogFile = {
  schemaVersion: string;
  source: string;
  updatedAt: string;
  products: LocalCatalogProduct[];
};

const CATALOG_SCHEMA_VERSION = "tablet-local-catalog.v1";

function catalogPath(): string {
  return path.join(process.cwd(), "data", "tablet-catalog.local.json");
}

function nowIso(): string {
  return new Date().toISOString();
}

function cleanText(value: unknown): string {
  return String(value ?? "").trim();
}

function makeProductId(sku: string, barcode?: string | null): string {
  const base = cleanText(sku || barcode || "product")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
  return `local-${base || "product"}`;
}

export function normalizeLocalCatalogProduct(input: LocalCatalogProductInput): LocalCatalogProduct {
  const sku = cleanText(input.sku).toUpperCase();
  const barcode = cleanText(input.barcode || "") || null;
  const name = cleanText(input.name);

  if (!sku && !barcode) {
    throw new Error("LOCAL_CATALOG_PRODUCT_REQUIRES_SKU_OR_BARCODE");
  }
  if (!name) {
    throw new Error("LOCAL_CATALOG_PRODUCT_REQUIRES_NAME");
  }
  if (!Number.isFinite(input.priceCents) || input.priceCents < 0) {
    throw new Error("LOCAL_CATALOG_PRODUCT_INVALID_PRICE");
  }

  const stockOnHand = Number.isFinite(input.stockOnHand) ? Number(input.stockOnHand) : 0;
  const lowStockThreshold = Number.isFinite(input.lowStockThreshold) ? Number(input.lowStockThreshold) : 0;

  return {
    id: cleanText(input.id) || makeProductId(sku, barcode),
    businessId: cleanText(input.businessId) || "local_business",
    sku,
    barcode,
    name,
    category: cleanText(input.category || "") || null,
    priceCents: Math.round(Number(input.priceCents)),
    stockOnHand: Math.round(stockOnHand),
    lowStockThreshold: Math.max(0, Math.round(lowStockThreshold)),
    isActive: input.isActive !== false,
    updatedAt: cleanText(input.updatedAt) || nowIso(),
  };
}

async function ensureCatalogFile(): Promise<void> {
  const file = catalogPath();
  await fs.mkdir(path.dirname(file), { recursive: true });
  try {
    await fs.access(file);
  } catch {
    const empty: LocalCatalogFile = {
      schemaVersion: CATALOG_SCHEMA_VERSION,
      source: "tablet-local-catalog-empty",
      updatedAt: nowIso(),
      products: [],
    };
    await fs.writeFile(file, JSON.stringify(empty, null, 2) + "\n", "utf8");
  }
}

export async function readLocalCatalogFile(): Promise<LocalCatalogFile> {
  await ensureCatalogFile();
  const raw = await fs.readFile(catalogPath(), "utf8");
  const parsed = JSON.parse(raw) as Partial<LocalCatalogFile>;
  const products = Array.isArray(parsed.products) ? parsed.products : [];
  return {
    schemaVersion: parsed.schemaVersion || CATALOG_SCHEMA_VERSION,
    source: parsed.source || "tablet-local-catalog",
    updatedAt: parsed.updatedAt || nowIso(),
    products: products.map((p) => normalizeLocalCatalogProduct(p)),
  };
}

export async function writeLocalCatalogFile(catalog: LocalCatalogFile): Promise<LocalCatalogFile> {
  const normalized: LocalCatalogFile = {
    schemaVersion: CATALOG_SCHEMA_VERSION,
    source: catalog.source || "tablet-local-catalog",
    updatedAt: nowIso(),
    products: catalog.products.map((p) => normalizeLocalCatalogProduct(p)),
  };
  await fs.mkdir(path.dirname(catalogPath()), { recursive: true });
  await fs.writeFile(catalogPath(), JSON.stringify(normalized, null, 2) + "\n", "utf8");
  return normalized;
}

export async function listLocalCatalogProducts(options?: { q?: string; includeInactive?: boolean }): Promise<LocalCatalogProduct[]> {
  const catalog = await readLocalCatalogFile();
  const q = cleanText(options?.q || "").toLowerCase();
  return catalog.products.filter((product) => {
    if (!options?.includeInactive && !product.isActive) return false;
    if (!q) return true;
    return [product.name, product.sku, product.barcode || "", product.category || ""]
      .join(" ")
      .toLowerCase()
      .includes(q);
  });
}

export async function resolveLocalCatalogProduct(code: string, options?: { includeInactive?: boolean }): Promise<LocalCatalogProduct | null> {
  const normalizedCode = cleanText(code).toLowerCase();
  if (!normalizedCode) return null;

  const catalog = await readLocalCatalogFile();
  return (
    catalog.products.find((product) => {
      if (!options?.includeInactive && !product.isActive) return false;
      return product.sku.toLowerCase() === normalizedCode || (product.barcode || "").toLowerCase() === normalizedCode;
    }) || null
  );
}

export async function importLocalCatalogProducts(input: { products: LocalCatalogProductInput[]; source?: string }): Promise<{
  imported: number;
  updated: number;
  skipped: number;
  products: LocalCatalogProduct[];
}> {
  const catalog = await readLocalCatalogFile();
  const byKey = new Map<string, LocalCatalogProduct>();
  for (const product of catalog.products) {
    byKey.set(product.sku, product);
    if (product.barcode) byKey.set(product.barcode, product);
  }

  let imported = 0;
  let updated = 0;
  let skipped = 0;

  for (const raw of input.products || []) {
    try {
      const product = normalizeLocalCatalogProduct(raw);
      const existing = byKey.get(product.sku) || (product.barcode ? byKey.get(product.barcode) : undefined);
      if (existing) {
        Object.assign(existing, product, { id: existing.id, updatedAt: nowIso() });
        updated += 1;
      } else {
        catalog.products.push(product);
        imported += 1;
      }
      byKey.set(product.sku, product);
      if (product.barcode) byKey.set(product.barcode, product);
    } catch {
      skipped += 1;
    }
  }

  await writeLocalCatalogFile({
    schemaVersion: CATALOG_SCHEMA_VERSION,
    source: input.source || "tablet-local-catalog-import",
    updatedAt: nowIso(),
    products: catalog.products,
  });

  return { imported, updated, skipped, products: catalog.products };
}
