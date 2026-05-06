import { BarcodeRepositoryPrisma } from "@/server/repositories/barcode-repository.prisma";
import { ProductRepositoryPrisma } from "@/server/repositories/product-repository.prisma";
import { StockRepositoryPrisma } from "@/server/repositories/stock-repository.prisma";

const products = new ProductRepositoryPrisma();
const barcodes = new BarcodeRepositoryPrisma();
const stock = new StockRepositoryPrisma();

function pesos(cents: number) {
  return cents / 100;
}

export async function getCatalogActiveSnapshot() {
  const activeProducts = await products.listActive(100);
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
    }))
  };
}

export async function getCriticalStockRows(limit = 25) {
  const rows = await stock.listCritical(limit);
  return rows.map((row) => ({
    sku: row.product.sku,
    producto: row.product.name,
    ubicacion: row.location,
    disponible: row.available,
    diasCobertura: row.daysCover,
    estado: row.daysCover < 1 ? "critico" : "riesgo"
  }));
}

export async function getBarcodeHealthRows() {
  const rows = await barcodes.listRecent(100);
  const byCategory = new Map<string, { productos: Set<string>; barcodes: number; activos: number }>();
  for (const barcode of rows) {
    const category = barcode.product.category;
    const current = byCategory.get(category) ?? { productos: new Set<string>(), barcodes: 0, activos: 0 };
    current.productos.add(barcode.productId);
    current.barcodes += 1;
    current.activos += barcode.product.isActive ? 1 : 0;
    byCategory.set(category, current);
  }
  return Array.from(byCategory.entries()).map(([categoria, row]) => ({
    categoria,
    productos: row.productos.size,
    barcodes: row.barcodes,
    promedio: row.productos.size ? Number((row.barcodes / row.productos.size).toFixed(2)) : 0,
    activos: row.activos
  }));
}
