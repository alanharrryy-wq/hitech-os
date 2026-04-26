import { pcMessages } from "@/lib/i18n/messages/es";
import { getCatalogActiveSnapshot, getCriticalStockRows } from "@/lib/services/catalog";
import { getProcurementConsole } from "@/lib/services/procurement";
import { getOutboxConsole } from "@/lib/services/sync";

export async function getPcDashboard() {
  const [catalog, criticalStock, procurement, outbox] = await Promise.all([
    getCatalogActiveSnapshot(),
    getCriticalStockRows(5),
    getProcurementConsole(),
    getOutboxConsole()
  ]);
  const pendingEvents = outbox.outboxPending;
  const openOrders = procurement.purchasePulse.slice(0, 4).map((order) => ({
    po: order.folio,
    supplier: order.supplier,
    lines: order.lines,
    eta: `$${order.total}`,
    status: order.status
  }));

  return {
    hero: {
      title: pcMessages.home.title,
      subtitle: pcMessages.home.subtitle,
      pills: [
        `SKUs activos (${catalog.snapshot.skusActivos})`,
        `Stock bajo (${criticalStock.length})`,
        `Outbox pendiente (${pendingEvents.length})`
      ]
    },
    summaryCards: [
      {
        label: "SKUs en inventario",
        value: String(catalog.snapshot.skusActivos),
        note: "Catálogo activo desde Prisma canónico.",
        icon: "◈",
        details: [
          { label: "Categorías", value: String(catalog.snapshot.categorias) },
          { label: "Barcodes/SKU", value: String(catalog.snapshot.promedioBarcodes) }
        ]
      },
      {
        label: "Stock bajo",
        value: String(criticalStock.length),
        note: "StockSnapshot con cobertura menor a dos días.",
        icon: "△",
        details: [
          { label: "Críticos", value: String(criticalStock.filter((row) => row.estado === "critico").length) },
          { label: "Riesgo", value: String(criticalStock.filter((row) => row.estado !== "critico").length) }
        ]
      },
      {
        label: "Compras abiertas",
        value: String(procurement.stats.ordenesAbiertas),
        note: "PurchaseOrder ordered + partial.",
        icon: "✦",
        details: [
          { label: "Proveedores", value: String(procurement.stats.proveedoresActivos) },
          { label: "Líneas", value: String(procurement.stats.lineasPlaneacion) }
        ]
      }
    ],
    categoryMix: catalog.categorySummary.map((row) => [row.categoria, row.skus] as const),
    lowStock: criticalStock.map((row) => ({
      sku: row.sku,
      name: row.producto,
      location: row.ubicacion,
      days: row.diasCobertura,
      status: row.estado === "critico" ? pcMessages.statuses.critical : pcMessages.statuses.risk
    })),
    openOrders,
    pendingSync: pendingEvents.slice(0, 5).map((event) => ({
      id: event.id,
      topic: event.topic,
      age: event.age,
      status: event.status === "failed" ? pcMessages.statuses.failed : pcMessages.statuses.pending
    })),
    actionCards: [
      {
        title: "Abrir catálogo activo",
        description: "Lee productos, barcodes y cobertura desde Prisma."
      },
      {
        title: "Revisar compras",
        description: "Valida PurchaseOrder y GoodsReceipt con totales gobernados."
      },
      {
        title: "Monitorear sincronización",
        description: "Consulta OutboxEvent canónico."
      }
    ],
    alertStrip: {
      title: "Prisma canónico activo en tablero",
      subtitle: "Las rutas críticas consumen repositorios Prisma, no arreglos demo."
    }
  };
}
