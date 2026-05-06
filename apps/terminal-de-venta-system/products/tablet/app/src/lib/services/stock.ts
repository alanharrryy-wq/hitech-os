import { ProductRepositoryPrisma } from "@/server/repositories/product-repository.prisma";

const productRepository = new ProductRepositoryPrisma();

function toneForDays(daysCover: number) {
  if (daysCover < 1) return "danger" as const;
  if (daysCover < 3) return "warn" as const;
  return "ok" as const;
}

function signalForDays(daysCover: number) {
  if (daysCover < 1) return "quiebre inminente";
  if (daysCover < 3) return "vigilar";
  return "estable";
}

export async function getStockConsole() {
  const products = await productRepository.listActive(25);
  const stockRows = products
    .flatMap((product) =>
      product.stockSnapshots.map((snapshot: { onHand: number; daysCover: number; location: string }) => ({
        sku: product.sku,
        name: product.name,
        onHand: snapshot.onHand,
        hoursLeft: Number((snapshot.daysCover * 24).toFixed(1)),
        daysCover: snapshot.daysCover,
        location: snapshot.location,
        barcodeOk: product.barcodes.length > 0,
        tone: toneForDays(snapshot.daysCover),
        signal: signalForDays(snapshot.daysCover)
      }))
    )
    .sort((a, b) => a.daysCover - b.daysCover);
  const hotSpot = stockRows[0];

  return {
    hotSpot: {
      sku: hotSpot?.sku ?? "-",
      name: hotSpot?.name ?? "sin stock activo",
      hoursLeft: hotSpot?.hoursLeft ?? 0,
      suggestedUnits: hotSpot ? Math.max(12, 24 - hotSpot.onHand) : 0,
      suggestedSource: hotSpot ? `reabasto hacia ${hotSpot.location}` : "-"
    },
    kpis: {
      monitoredSkus: products.length,
      stockouts: stockRows.filter((row) => row.daysCover < 1).length,
      lowCoverage: stockRows.filter((row) => row.daysCover < 3).length,
      barcodeIssues: stockRows.filter((row) => !row.barcodeOk).length
    },
    watchlist: stockRows.slice(0, 8).map((row) => ({
      sku: row.sku,
      name: row.name,
      onHand: row.onHand,
      velocity: `${(row.onHand / Math.max(row.hoursLeft, 1)).toFixed(1)} uds`,
      signal: row.signal,
      tone: row.tone
    })),
    replenishment: stockRows.slice(0, 4).map((row) => ({
      sku: row.sku,
      recommendedUnits: Math.max(12, 24 - row.onHand),
      coverage: `${row.hoursLeft} h`,
      source: `ubicación ${row.location}`
    })),
    barcodeAlerts: stockRows
      .filter((row) => !row.barcodeOk)
      .map((row) => ({
        title: "SKU activo sin barcode",
        level: "alerta",
        tone: "warn" as const,
        description: `${row.sku} no tiene Barcode canónico.`,
        action: "Capturar Barcode antes del siguiente pico."
      })),
    aislePulse: Array.from(new Set(products.map((product) => product.category))).map((category) => {
      const categoryRows = stockRows.filter((row) => products.find((product) => product.sku === row.sku)?.category === category);
      const pressure = Math.min(100, categoryRows.filter((row) => row.tone !== "ok").length * 35);
      return {
        name: category,
        note: "lectura desde Product y StockSnapshot",
        pressure,
        stockouts: categoryRows.filter((row) => row.daysCover < 1).length,
        lowCoverage: categoryRows.filter((row) => row.daysCover < 3).length,
        velocity: `${categoryRows.length} SKUs`,
        signal: pressure > 70 ? "presion alta" : pressure > 0 ? "vigilar" : "estable",
        tone: pressure > 70 ? ("danger" as const) : pressure > 0 ? ("warn" as const) : ("ok" as const)
      };
    })
  };
}
