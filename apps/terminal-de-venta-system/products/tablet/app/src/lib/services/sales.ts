export function getRecentTickets() {
  return [
    { folio: "TK-90231", total: 182, items: 4, cashier: "Sandra", status: "cerrado", tone: "ok" as const },
    { folio: "TK-90230", total: 74, items: 2, cashier: "Leo", status: "cerrado", tone: "ok" as const },
    { folio: "TK-90229", total: 231, items: 6, cashier: "Sandra", status: "ajuste por devolucion", tone: "warn" as const },
    { folio: "TK-90228", total: 59, items: 1, cashier: "Mauro", status: "cerrado", tone: "ok" as const },
    { folio: "TK-90227", total: 148, items: 3, cashier: "Yari", status: "pendiente de sync", tone: "warn" as const },
    { folio: "TK-90226", total: 309, items: 8, cashier: "Sandra", status: "revision manual", tone: "danger" as const }
  ];
}

export function getSalesConsole() {
  return {
    shift: {
      cashier: "Sandra M.",
      openedAt: "07:00"
    },
    queue: {
      waitingTickets: 3,
      waitingItems: 17
    },
    kpis: {
      netSales: 18450,
      tickets: 126,
      avgTicket: 146.4,
      unitsPerTicket: 2.9
    },
    recentTickets: getRecentTickets(),
    topProducts: [
      { sku: "REF-355ML", name: "Refresco 355 ml", qty: 34, revenue: 1020 },
      { sku: "BOT-600ML", name: "Agua 600 ml", qty: 28, revenue: 560 },
      { sku: "PAP-ADOBO", name: "Papas adobadas", qty: 21, revenue: 735 },
      { sku: "CAF-AMER", name: "Cafe americano", qty: 18, revenue: 666 },
      { sku: "CHO-CLAS", name: "Chocolate clasico", qty: 16, revenue: 432 }
    ],
    alerts: [
      {
        title: "SKU sin barcode operativo",
        level: "vigilar",
        tone: "warn" as const,
        description: "2 articulos estan entrando por captura manual y eso le mete tierra al flujo.",
        action: "accion sugerida: validar barcode antes del siguiente cierre"
      },
      {
        title: "Diferencia de efectivo en turno",
        level: "critico",
        tone: "danger" as const,
        description: "La caja trae una variacion de $86 frente al corte parcial.",
        action: "accion sugerida: revisar ultimos 5 tickets con efectivo"
      },
      {
        title: "Fila bajo control",
        level: "ok",
        tone: "ok" as const,
        description: "El tiempo promedio de venta se mantiene debajo de 70 segundos.",
        action: "accion sugerida: sostener shortcut de recobro rapido"
      }
    ],
    stockSignals: [
      { sku: "PAP-ADOBO", name: "Papas adobadas", onHand: 3, coverage: "1.8 h", signal: "quiebre inminente", tone: "danger" as const },
      { sku: "REF-355ML", name: "Refresco 355 ml", onHand: 5, coverage: "0.9 h", signal: "presion alta", tone: "danger" as const },
      { sku: "BOT-1L", name: "Agua 1 L", onHand: 9, coverage: "2.1 h", signal: "vigilar", tone: "warn" as const },
      { sku: "GOM-MIX", name: "Gomitas mix", onHand: 11, coverage: "5.2 h", signal: "estable", tone: "ok" as const }
    ],
    replenishment: [
      { sku: "PAP-ADOBO", source: "bodega fria B-2", units: 24, note: "combo de impulso en rojo" },
      { sku: "REF-355ML", source: "rack rapido R-1", units: 36, note: "pico de salida en mostrador" },
      { sku: "BOT-1L", source: "pallet lateral L-3", units: 18, note: "captura manual repetida" }
    ]
  };
}
