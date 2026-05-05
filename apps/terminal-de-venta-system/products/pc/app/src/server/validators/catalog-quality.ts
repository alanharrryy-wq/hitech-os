import type { CatalogIssue, CatalogProductRecord } from "@/modules/catalog/types";

const STALE_PRICE_DAYS = 45;

export function normalizeBarcode(code: string | null | undefined) {
  return String(code ?? "").trim();
}

export function hasMissingBarcode(product: { barcodes?: string[]; barcode?: string | null; isActive: boolean }) {
  const legacyBarcode = normalizeBarcode(product.barcode);
  const barcodes = product.barcodes ?? (legacyBarcode ? [legacyBarcode] : []);
  return product.isActive && barcodes.map(normalizeBarcode).filter(Boolean).length === 0;
}

export function isPriceStale(updatedAt: string | Date | null | undefined, now = new Date(), maxAgeDays = STALE_PRICE_DAYS) {
  if (!updatedAt) return true;
  const updated = updatedAt instanceof Date ? updatedAt : new Date(updatedAt);
  if (Number.isNaN(updated.getTime())) return true;
  const ageMs = now.getTime() - updated.getTime();
  return ageMs > maxAgeDays * 24 * 60 * 60 * 1000;
}

export function findDuplicateBarcodes(products: Array<{ sku: string; name: string; barcodes: string[] }>) {
  const seen = new Map<string, Array<{ sku: string; name: string }>>();
  for (const product of products) {
    for (const raw of product.barcodes) {
      const code = normalizeBarcode(raw);
      if (!code) continue;
      const rows = seen.get(code) ?? [];
      rows.push({ sku: product.sku, name: product.name });
      seen.set(code, rows);
    }
  }

  return Array.from(seen.entries())
    .filter(([, rows]) => rows.length > 1)
    .map(([code, rows]) => ({ code, products: rows }));
}

export function buildCatalogIssues(products: CatalogProductRecord[], now = new Date()): CatalogIssue[] {
  const duplicateGroups = findDuplicateBarcodes(products);
  const duplicateBySku = new Map<string, string[]>();

  for (const group of duplicateGroups) {
    for (const row of group.products) {
      const codes = duplicateBySku.get(row.sku) ?? [];
      codes.push(group.code);
      duplicateBySku.set(row.sku, codes);
    }
  }

  return products.flatMap((product) => {
    const issues: CatalogIssue[] = [];

    if (hasMissingBarcode(product)) {
      issues.push({
        type: "missing_barcode",
        severity: "ALTO",
        sku: product.sku,
        productName: product.name,
        label: "Sin barcode",
        detail: "Producto activo sin barcode operativo.",
        recommendedAction: "Capturar o importar barcode antes de operación en caja/recepción."
      });
    }

    const duplicates = duplicateBySku.get(product.sku) ?? [];
    if (duplicates.length) {
      issues.push({
        type: "duplicate_barcode",
        severity: "ALTO",
        sku: product.sku,
        productName: product.name,
        label: "Barcode duplicado",
        detail: `Comparte código(s): ${Array.from(new Set(duplicates)).join(", ")}.`,
        recommendedAction: "Resolver duplicidad antes de sync o escaneo operativo."
      });
    }

    if (!product.isActive) {
      issues.push({
        type: "inactive_product",
        severity: "MEDIO",
        sku: product.sku,
        productName: product.name,
        label: "Producto inactivo",
        detail: "El producto aparece en catálogo visible pero no está activo.",
        recommendedAction: "Confirmar si debe ocultarse, reactivarse o mantenerse sólo para auditoría."
      });
    }

    if (isPriceStale(product.updatedAt, now)) {
      issues.push({
        type: "stale_price",
        severity: "MEDIO",
        sku: product.sku,
        productName: product.name,
        label: "Precio viejo",
        detail: "La última actualización supera la política operativa de 45 días.",
        recommendedAction: "Revisar precio/costo antes de compras, recepción o promociones."
      });
    }

    return issues;
  });
}
