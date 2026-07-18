import { BarcodeRepositoryPrisma } from "@/server/repositories/barcode-repository.prisma";
import { ProductRepositoryPrisma } from "@/server/repositories/product-repository.prisma";
import { StockRepositoryPrisma } from "@/server/repositories/stock-repository.prisma";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";

const products = new ProductRepositoryPrisma();
const barcodes = new BarcodeRepositoryPrisma();
const stock = new StockRepositoryPrisma();

export type PcDataNotice = {
  title: string;
  detail: string;
  code: "pc_db_unavailable";
};

function pesos(cents: number) {
  return cents / 100;
}

function safeErrorMessage(error: unknown) {
  if (!(error instanceof Error)) return "La lectura local no respondió.";
  return error.message
    .replace(/[A-Z]:\\[^\s)]+/g, "<LOCAL_PATH>")
    .replace(/file:[^\s)]+/g, "file:<LOCAL_DB>")
    .slice(0, 220);
}

function buildDataNotice(error: unknown): PcDataNotice {
  return {
    title: "Datos locales no disponibles",
    detail: `La pantalla quedó en estado vacío honesto para evitar el overlay rojo de desarrollo. Causa: ${safeErrorMessage(error)}`,
    code: "pc_db_unavailable"
  };
}

export async function getCatalogActiveSnapshot() {
  try {
    const businessId = await resolvePcBusinessScope();
    const activeProducts = await products.listActive(businessId, 100);
    const categories = new Map<string, { skus: number; activos: number; price: number; cost: number; barcodes: number }>();
    for (const product of activeProducts) {
      const current = categories.get(product.category) ?? { skus: 0, activos: 0, price: 0, cost: 0, barcodes: 0 };
      current.skus += 1;
      current.activos += product.isActive ? 1 : 0;
      current.price += product.priceCents;
      current.cost += product.costCents;
      current.barcodes += product.barcodes.length;
      categories.set(product.category, current);
    }
    const critical = activeProducts.flatMap((product) => product.stockSnapshots).filter((row) => row.daysCover < 2).length;
    const totalBarcodes = activeProducts.reduce((acc, product) => acc + product.barcodes.length, 0);
    return {
      snapshot: {
        categorias: categories.size,
        skusActivos: activeProducts.length,
        filasCriticas: critical,
        promedioBarcodes: activeProducts.length ? Number((totalBarcodes / activeProducts.length).toFixed(2)) : 0
      },
      categorySummary: Array.from(categories.entries()).map(([categoria, row]) => ({
        categoria,
        skus: row.skus,
        activos: row.activos,
        precioPromedio: row.skus ? pesos(row.price / row.skus).toFixed(2) : "0.00",
        costoPromedio: row.skus ? pesos(row.cost / row.skus).toFixed(2) : "0.00"
      })),
      notice: null as PcDataNotice | null
    };
  } catch (error) {
    return {
      snapshot: {
        categorias: 0,
        skusActivos: 0,
        filasCriticas: 0,
        promedioBarcodes: 0
      },
      categorySummary: [] as Array<{ categoria: string; skus: number; activos: number; precioPromedio: string; costoPromedio: string }>,
      notice: buildDataNotice(error)
    };
  }
}

export async function getCriticalStockRows(input: { limit?: number; urgency?: string } = {}) {
  try {
    const businessId = await resolvePcBusinessScope();
    const urgency = input.urgency === "today" || input.urgency === "3days" || input.urgency === "week" ? input.urgency : "all";
    const maxDaysCover = urgency === "today" ? 1 : urgency === "3days" ? 3 : urgency === "week" ? 7 : 2;
    const rows = await stock.listCritical(businessId, input.limit ?? 25, maxDaysCover);
    return {
      rows: rows.map((row) => ({
        sku: row.product.sku,
        producto: row.product.name,
        ubicacion: row.location,
        disponible: row.available,
        diasCobertura: row.daysCover,
        estado: row.daysCover < 1 ? "critico" : "riesgo"
      })),
      notice: null as PcDataNotice | null
    };
  } catch (error) {
    return {
      rows: [] as Array<{ sku: string; producto: string; ubicacion: string; disponible: number; diasCobertura: number; estado: string }>,
      notice: buildDataNotice(error)
    };
  }
}

export async function getBarcodeHealthRows() {
  try {
    const businessId = await resolvePcBusinessScope();
    const rows = await barcodes.listRecent(businessId, 100);
    const byCategory = new Map<string, { productos: Set<string>; barcodes: number; activos: number }>();
    for (const barcode of rows) {
      const category = barcode.product.category;
      const current = byCategory.get(category) ?? { productos: new Set<string>(), barcodes: 0, activos: 0 };
      current.productos.add(barcode.productId);
      current.barcodes += 1;
      current.activos += barcode.product.isActive ? 1 : 0;
      byCategory.set(category, current);
    }
    return {
      rows: Array.from(byCategory.entries()).map(([categoria, row]) => ({
        categoria,
        productos: row.productos.size,
        barcodes: row.barcodes,
        promedio: row.productos.size ? Number((row.barcodes / row.productos.size).toFixed(2)) : 0,
        activos: row.activos
      })),
      notice: null as PcDataNotice | null
    };
  } catch (error) {
    return {
      rows: [] as Array<{ categoria: string; productos: number; barcodes: number; promedio: number; activos: number }>,
      notice: buildDataNotice(error)
    };
  }
}
