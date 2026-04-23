export function getStockConsole() {
  return {
    hotSpot: {
      sku: "PAP-ADOBO",
      name: "Papas adobadas",
      hoursLeft: 1.8,
      suggestedUnits: 24,
      suggestedSource: "reabasto desde bodega fría B-2"
    },
    kpis: {
      monitoredSkus: 84,
      stockouts: 6,
      lowCoverage: 14,
      barcodeIssues: 5
    },
    watchlist: [
      { sku: "PAP-ADOBO", name: "Papas adobadas", onHand: 3, velocity: "7.2 uds", signal: "quiebre inminente", tone: "danger" as const },
      { sku: "BOT-1L", name: "Agua 1 L", onHand: 9, velocity: "6.4 uds", signal: "vigilar", tone: "warn" as const },
      { sku: "REF-355ML", name: "Refresco 355 ml", onHand: 5, velocity: "9.1 uds", signal: "caliente", tone: "danger" as const },
      { sku: "GOM-MIX", name: "Gomitas mix", onHand: 11, velocity: "3.8 uds", signal: "estable", tone: "ok" as const },
      { sku: "CAF-AMER", name: "Cafe americano", onHand: 7, velocity: "4.6 uds", signal: "vigilar", tone: "warn" as const }
    ],
    replenishment: [
      { sku: "PAP-ADOBO", recommendedUnits: 24, coverage: "1.8 h", source: "bodega fria B-2" },
      { sku: "REF-355ML", recommendedUnits: 36, coverage: "0.9 h", source: "rack rapido R-1" },
      { sku: "BOT-1L", recommendedUnits: 18, coverage: "2.1 h", source: "pallet lateral L-3" },
      { sku: "CHO-CLAS", recommendedUnits: 12, coverage: "3.7 h", source: "reserva mostrador" }
    ],
    barcodeAlerts: [
      {
        title: "SKU activo sin barcode limpio",
        level: "alerta",
        tone: "warn" as const,
        description: "BOT-1L sigue entrando por captura manual en 4 tickets del turno y eso ya huele a tropiezo repetido.",
        action: "accion sugerida: reimprimir etiqueta y validar lectura antes del siguiente pico"
      },
      {
        title: "Precio desfasado en anaquel",
        level: "critico",
        tone: "danger" as const,
        description: "CHO-CLAS trae diferencia entre precio visible y precio de caja. Eso luego acaba en cara larga y devolucion.",
        action: "accion sugerida: bloquear venta asistida hasta confirmar precio maestro"
      },
      {
        title: "Duplicidad de barcode controlada",
        level: "ok",
        tone: "ok" as const,
        description: "El cruce REF-355ML contra promo temporal ya fue aislado y no esta pegando a la fila.",
        action: "accion sugerida: mantener monitoreo sin frenar operacion"
      }
    ],
    aislePulse: [
      { name: "bebidas frias", note: "alto arrastre en mostrador y ruta", pressure: 86, stockouts: 2, lowCoverage: 5, velocity: "18.3 uds", signal: "presion alta", tone: "danger" as const },
      { name: "botanas", note: "canasta rapida y combo de impulso", pressure: 71, stockouts: 3, lowCoverage: 4, velocity: "13.8 uds", signal: "vigilar", tone: "warn" as const },
      { name: "cafe y caloricos", note: "rotacion estable con un pico por la manana", pressure: 42, stockouts: 0, lowCoverage: 3, velocity: "6.4 uds", signal: "estable", tone: "ok" as const }
    ]
  };
}
