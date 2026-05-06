import { PurchaseOrderRepositoryPrisma } from "@/server/repositories/purchase-order-repository.prisma";

const procurement = new PurchaseOrderRepositoryPrisma();

function pesos(cents: number) {
  return cents / 100;
}

export async function getProcurementConsole() {
  const [orders, receipts] = await Promise.all([
    procurement.listOpen(25),
    procurement.listRecentReceipts(25)
  ]);
  const suppliers = new Map<string, { total: number; partial: number; received: number }>();
  for (const order of orders) {
    const current = suppliers.get(order.supplier.name) ?? { total: 0, partial: 0, received: 0 };
    current.total += 1;
    current.partial += order.status === "partial" ? 1 : 0;
    suppliers.set(order.supplier.name, current);
  }
  for (const receipt of receipts) {
    const current = suppliers.get(receipt.supplier.name) ?? { total: 0, partial: 0, received: 0 };
    current.received += 1;
    suppliers.set(receipt.supplier.name, current);
  }

  return {
    stats: {
      ordenesAbiertas: orders.length,
      proveedoresActivos: suppliers.size,
      recepcionesConIncidencia: receipts.filter((receipt) => receipt.status !== "posted").length,
      lineasPlaneacion: orders.reduce((acc, order) => acc + order.lines.length, 0),
      topProveedor: Array.from(suppliers.entries()).sort((a, b) => b[1].total - a[1].total)[0]?.[0] ?? "-"
    },
    purchasePulse: orders.map((order) => ({
      folio: order.folio,
      supplier: order.supplier.name,
      status: order.status,
      total: pesos(order.totalCents).toFixed(2),
      lines: order.lines.length
    })),
    receivingIncidents: receipts.map((receipt) => ({
      purchaseId: receipt.purchaseOrderId,
      folio: receipt.folio,
      supplier: receipt.supplier.name,
      receivedAt: new Date(receipt.receivedAt).toISOString(),
      lines: receipt.lines.length,
      total: pesos(receipt.totalCents).toFixed(2),
      status: receipt.status
    })),
    supplierHeat: Array.from(suppliers.entries()).map(([supplier, row]) => ({
      supplier,
      total_orders: row.total,
      partial_count: row.partial,
      received_count: row.received
    }))
  };
}
