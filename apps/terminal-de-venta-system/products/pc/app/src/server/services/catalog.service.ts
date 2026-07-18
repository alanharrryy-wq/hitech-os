import { CatalogRepository } from "@/server/repositories/catalog.repository";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { buildCatalogIssues } from "@/server/validators/catalog-quality";
import type { CatalogFilters, CatalogIssueFilter, CatalogStatusFilter, CatalogWorkspace } from "@/modules/catalog/types";

const repository = new CatalogRepository();

function normalizeStatus(value: string): CatalogStatusFilter {
  return value === "active" || value === "inactive" ? value : "all";
}

function normalizeIssue(value: string): CatalogIssueFilter {
  return ["missing_barcode", "duplicate_barcode", "inactive_product", "stale_price"].includes(value) ? (value as CatalogIssueFilter) : "all";
}

function normalizeFilters(input: Partial<Record<keyof CatalogFilters, string>>): CatalogFilters {
  return {
    q: String(input.q ?? "").trim().slice(0, 80),
    status: normalizeStatus(String(input.status ?? "all")),
    category: String(input.category ?? "all") || "all",
    issue: normalizeIssue(String(input.issue ?? "all")),
    selectedSku: String(input.selectedSku ?? "").trim()
  };
}

function summarize(products: Awaited<ReturnType<CatalogRepository["listProducts"]>>) {
  const activeProducts = products.filter((product) => product.isActive).length;
  const barcodeCount = products.reduce((acc, product) => acc + product.barcodes.length, 0);
  const missingBarcodeCount = products.filter((product) => product.isActive && product.barcodes.length === 0).length;
  const duplicateBarcodeCount = products.flatMap((product) => product.issues).filter((issue) => issue.type === "duplicate_barcode").length;
  const stalePriceCount = products.flatMap((product) => product.issues).filter((issue) => issue.type === "stale_price").length;

  return {
    totalProducts: products.length,
    activeProducts,
    inactiveProducts: products.length - activeProducts,
    categories: new Set(products.map((product) => product.category)).size,
    barcodeCount,
    missingBarcodeCount,
    duplicateBarcodeCount,
    stalePriceCount
  };
}

export async function getCatalogWorkspace(input: Partial<Record<keyof CatalogFilters, string>>): Promise<CatalogWorkspace> {
  const filters = normalizeFilters(input);
  const generatedAt = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date());

  try {
    const businessId = await resolvePcBusinessScope();
    const [rawProducts, categories] = await Promise.all([
      repository.listProducts(businessId, filters, 250),
      repository.listCategories(businessId)
    ]);

    const issues = buildCatalogIssues(rawProducts);
    const productsWithIssues = rawProducts.map((product) => ({
      ...product,
      issues: issues.filter((issue) => issue.sku === product.sku)
    }));

    const filteredProducts = filters.issue === "all"
      ? productsWithIssues
      : productsWithIssues.filter((product) => product.issues.some((issue) => issue.type === filters.issue));

    const exceptions = filteredProducts.flatMap((product) => product.issues);
    const selectedProduct = filters.selectedSku
      ? filteredProducts.find((product) => product.sku === filters.selectedSku) ?? null
      : null;

    return {
      filters,
      summary: summarize(productsWithIssues),
      categories,
      products: filteredProducts,
      exceptions,
      selectedProduct,
      meta: {
        source: "canonical_prisma",
        confidence: "real",
        persistence: "available",
        generatedAt,
        warnings: []
      }
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido leyendo Prisma.";
    return {
      filters,
      summary: {
        totalProducts: 0,
        activeProducts: 0,
        inactiveProducts: 0,
        categories: 0,
        barcodeCount: 0,
        missingBarcodeCount: 0,
        duplicateBarcodeCount: 0,
        stalePriceCount: 0
      },
      categories: [],
      products: [],
      exceptions: [],
      selectedProduct: null,
      meta: {
        source: "fallback_empty",
        confidence: "blocked",
        persistence: "unavailable",
        generatedAt,
        warnings: ["No se pudo cargar la información. Revisa la sincronización o la base local."]
      }
    };
  }
}
