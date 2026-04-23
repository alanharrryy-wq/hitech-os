export const pcI06DashboardData = {
  "cards": [
    {
      "id": "ventas-netas-demo",
      "label": "Ventas netas demo",
      "valueMx": 2217775.29,
      "format": "currency",
      "confidence": "proxy_movimientos_sale",
      "note": "Derivada de movimientos reason=sale; reemplazar por verdad POS cuando exista feed de tickets."
    },
    {
      "id": "tickets-demo",
      "label": "Tickets demo",
      "value": 23075,
      "format": "integer",
      "confidence": "proxy_modelo_ticket",
      "note": "Modelo de demo con 2.6 unidades por ticket sobre salidas de venta."
    },
    {
      "id": "ticket-promedio-demo",
      "label": "Ticket promedio demo",
      "valueMx": 97.48,
      "format": "currency",
      "confidence": "proxy_modelo_ticket",
      "note": "Misma base proxy que tickets demo."
    },
    {
      "id": "quiebres-stock",
      "label": "Quiebres de stock",
      "value": 430,
      "format": "integer",
      "confidence": "snapshot_real",
      "note": "Slots de inventario con available <= 0."
    },
    {
      "id": "exactitud-inventario",
      "label": "Exactitud de inventario",
      "valuePct": 11.0,
      "format": "percent",
      "confidence": "audit_real",
      "note": "Conteos exactos sobre total de conteos auditados."
    },
    {
      "id": "merma-acumulada",
      "label": "Merma acumulada",
      "valueMx": 1415970.05,
      "format": "currency",
      "confidence": "movement_damage_real",
      "note": "Proxy operativo basado en movimientos reason=damage."
    },
    {
      "id": "fill-rate",
      "label": "Fill rate",
      "valuePct": 77.14,
      "format": "percent",
      "confidence": "po_vs_receipt_proxy",
      "note": "Recibos sobre órdenes por proveedor."
    },
    {
      "id": "outbox-fallido",
      "label": "Eventos outbox fallidos",
      "value": 1000,
      "format": "integer",
      "confidence": "outbox_real",
      "note": "Eventos pendientes de corrección o reenvío."
    }
  ],
  "topSkus": [
    {
      "sku": "SKU-00480",
      "name": "Bebidas producto 480",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 3360.0,
      "grossMarginMx": 1243.2,
      "saleEvents": 8
    },
    {
      "sku": "SKU-02108",
      "name": "Farmacia producto 2108",
      "category": "Farmacia",
      "unitsSold": 56,
      "grossSalesMx": 3360.0,
      "grossMarginMx": 1243.2,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03736",
      "name": "Snacks producto 3736",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 3360.0,
      "grossMarginMx": 1243.2,
      "saleEvents": 8
    },
    {
      "sku": "SKU-01404",
      "name": "Limpieza producto 1404",
      "category": "Limpieza",
      "unitsSold": 56,
      "grossSalesMx": 3290.0,
      "grossMarginMx": 1217.44,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03032",
      "name": "Lácteos producto 3032",
      "category": "Lácteos",
      "unitsSold": 56,
      "grossSalesMx": 3290.0,
      "grossMarginMx": 1217.44,
      "saleEvents": 8
    },
    {
      "sku": "SKU-04660",
      "name": "Bebidas producto 4660",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 3290.0,
      "grossMarginMx": 1217.44,
      "saleEvents": 8
    },
    {
      "sku": "SKU-00700",
      "name": "Bebidas producto 700",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 3220.0,
      "grossMarginMx": 1191.68,
      "saleEvents": 8
    },
    {
      "sku": "SKU-02328",
      "name": "Farmacia producto 2328",
      "category": "Farmacia",
      "unitsSold": 56,
      "grossSalesMx": 3220.0,
      "grossMarginMx": 1191.68,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03956",
      "name": "Snacks producto 3956",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 3220.0,
      "grossMarginMx": 1191.68,
      "saleEvents": 8
    },
    {
      "sku": "SKU-01624",
      "name": "Limpieza producto 1624",
      "category": "Limpieza",
      "unitsSold": 56,
      "grossSalesMx": 3150.0,
      "grossMarginMx": 1165.92,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03252",
      "name": "Lácteos producto 3252",
      "category": "Lácteos",
      "unitsSold": 56,
      "grossSalesMx": 3150.0,
      "grossMarginMx": 1165.92,
      "saleEvents": 8
    },
    {
      "sku": "SKU-04880",
      "name": "Bebidas producto 4880",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 3150.0,
      "grossMarginMx": 1165.92,
      "saleEvents": 8
    },
    {
      "sku": "SKU-00920",
      "name": "Bebidas producto 920",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 3080.0,
      "grossMarginMx": 1139.6,
      "saleEvents": 8
    },
    {
      "sku": "SKU-02548",
      "name": "Farmacia producto 2548",
      "category": "Farmacia",
      "unitsSold": 56,
      "grossSalesMx": 3080.0,
      "grossMarginMx": 1139.6,
      "saleEvents": 8
    },
    {
      "sku": "SKU-04176",
      "name": "Snacks producto 4176",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 3080.0,
      "grossMarginMx": 1139.6,
      "saleEvents": 8
    },
    {
      "sku": "SKU-00216",
      "name": "Snacks producto 216",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 3010.0,
      "grossMarginMx": 1113.84,
      "saleEvents": 8
    },
    {
      "sku": "SKU-01844",
      "name": "Limpieza producto 1844",
      "category": "Limpieza",
      "unitsSold": 56,
      "grossSalesMx": 3010.0,
      "grossMarginMx": 1113.84,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03472",
      "name": "Lácteos producto 3472",
      "category": "Lácteos",
      "unitsSold": 56,
      "grossSalesMx": 3010.0,
      "grossMarginMx": 1113.84,
      "saleEvents": 8
    },
    {
      "sku": "SKU-01140",
      "name": "Bebidas producto 1140",
      "category": "Bebidas",
      "unitsSold": 56,
      "grossSalesMx": 2940.0,
      "grossMarginMx": 1088.08,
      "saleEvents": 8
    },
    {
      "sku": "SKU-02768",
      "name": "Farmacia producto 2768",
      "category": "Farmacia",
      "unitsSold": 56,
      "grossSalesMx": 2940.0,
      "grossMarginMx": 1088.08,
      "saleEvents": 8
    },
    {
      "sku": "SKU-04396",
      "name": "Snacks producto 4396",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 2940.0,
      "grossMarginMx": 1088.08,
      "saleEvents": 8
    },
    {
      "sku": "SKU-00436",
      "name": "Snacks producto 436",
      "category": "Snacks",
      "unitsSold": 56,
      "grossSalesMx": 2870.0,
      "grossMarginMx": 1062.32,
      "saleEvents": 8
    },
    {
      "sku": "SKU-02064",
      "name": "Limpieza producto 2064",
      "category": "Limpieza",
      "unitsSold": 56,
      "grossSalesMx": 2870.0,
      "grossMarginMx": 1062.32,
      "saleEvents": 8
    },
    {
      "sku": "SKU-03692",
      "name": "Lácteos producto 3692",
      "category": "Lácteos",
      "unitsSold": 56,
      "grossSalesMx": 2870.0,
      "grossMarginMx": 1062.32,
      "saleEvents": 8
    }
  ],
  "categoryHealth": [
    {
      "category": "Lácteos",
      "products": 1000,
      "stockValueMx": 2568150.0,
      "stockoutSlots": 71,
      "avgDaysCover": 6.14
    },
    {
      "category": "Limpieza",
      "products": 1000,
      "stockValueMx": 2530428.75,
      "stockoutSlots": 36,
      "avgDaysCover": 5.92
    },
    {
      "category": "Snacks",
      "products": 1000,
      "stockValueMx": 2488925.0,
      "stockoutSlots": 36,
      "avgDaysCover": 5.95
    },
    {
      "category": "Farmacia",
      "products": 1000,
      "stockValueMx": 2456930.0,
      "stockoutSlots": 72,
      "avgDaysCover": 5.77
    },
    {
      "category": "Bebidas",
      "products": 1000,
      "stockValueMx": 2235481.25,
      "stockoutSlots": 215,
      "avgDaysCover": 5.25
    }
  ],
  "stockouts": [
    {
      "sku": "SKU-00000",
      "name": "Bebidas producto 0",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:00:00"
    },
    {
      "sku": "SKU-00000",
      "name": "Bebidas producto 0",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:00:00"
    },
    {
      "sku": "SKU-00018",
      "name": "Farmacia producto 18",
      "category": "Farmacia",
      "location": "RACK-3",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:18:00"
    },
    {
      "sku": "SKU-00035",
      "name": "Bebidas producto 35",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:35:00"
    },
    {
      "sku": "SKU-00047",
      "name": "Lácteos producto 47",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:47:00"
    },
    {
      "sku": "SKU-00053",
      "name": "Farmacia producto 53",
      "category": "Farmacia",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T08:53:00"
    },
    {
      "sku": "SKU-00070",
      "name": "Bebidas producto 70",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:10:00"
    },
    {
      "sku": "SKU-00070",
      "name": "Bebidas producto 70",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:10:00"
    },
    {
      "sku": "SKU-00071",
      "name": "Snacks producto 71",
      "category": "Snacks",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:11:00"
    },
    {
      "sku": "SKU-00094",
      "name": "Limpieza producto 94",
      "category": "Limpieza",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:34:00"
    },
    {
      "sku": "SKU-00105",
      "name": "Bebidas producto 105",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:45:00"
    },
    {
      "sku": "SKU-00117",
      "name": "Lácteos producto 117",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T09:57:00"
    },
    {
      "sku": "SKU-00140",
      "name": "Bebidas producto 140",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T10:20:00"
    },
    {
      "sku": "SKU-00140",
      "name": "Bebidas producto 140",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T10:20:00"
    },
    {
      "sku": "SKU-00158",
      "name": "Farmacia producto 158",
      "category": "Farmacia",
      "location": "RACK-3",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T10:38:00"
    },
    {
      "sku": "SKU-00175",
      "name": "Bebidas producto 175",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T10:55:00"
    },
    {
      "sku": "SKU-00187",
      "name": "Lácteos producto 187",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:07:00"
    },
    {
      "sku": "SKU-00193",
      "name": "Farmacia producto 193",
      "category": "Farmacia",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:13:00"
    },
    {
      "sku": "SKU-00210",
      "name": "Bebidas producto 210",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:30:00"
    },
    {
      "sku": "SKU-00210",
      "name": "Bebidas producto 210",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:30:00"
    },
    {
      "sku": "SKU-00211",
      "name": "Snacks producto 211",
      "category": "Snacks",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:31:00"
    },
    {
      "sku": "SKU-00234",
      "name": "Limpieza producto 234",
      "category": "Limpieza",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T11:54:00"
    },
    {
      "sku": "SKU-00245",
      "name": "Bebidas producto 245",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T12:05:00"
    },
    {
      "sku": "SKU-00257",
      "name": "Lácteos producto 257",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T12:17:00"
    },
    {
      "sku": "SKU-00280",
      "name": "Bebidas producto 280",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T12:40:00"
    },
    {
      "sku": "SKU-00280",
      "name": "Bebidas producto 280",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T12:40:00"
    },
    {
      "sku": "SKU-00298",
      "name": "Farmacia producto 298",
      "category": "Farmacia",
      "location": "RACK-3",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T12:58:00"
    },
    {
      "sku": "SKU-00315",
      "name": "Bebidas producto 315",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:15:00"
    },
    {
      "sku": "SKU-00327",
      "name": "Lácteos producto 327",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:27:00"
    },
    {
      "sku": "SKU-00333",
      "name": "Farmacia producto 333",
      "category": "Farmacia",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:33:00"
    },
    {
      "sku": "SKU-00350",
      "name": "Bebidas producto 350",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:50:00"
    },
    {
      "sku": "SKU-00350",
      "name": "Bebidas producto 350",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:50:00"
    },
    {
      "sku": "SKU-00351",
      "name": "Snacks producto 351",
      "category": "Snacks",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T13:51:00"
    },
    {
      "sku": "SKU-00374",
      "name": "Limpieza producto 374",
      "category": "Limpieza",
      "location": "B-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T14:14:00"
    },
    {
      "sku": "SKU-00385",
      "name": "Bebidas producto 385",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T14:25:00"
    },
    {
      "sku": "SKU-00397",
      "name": "Lácteos producto 397",
      "category": "Lácteos",
      "location": "BAR-1",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T14:37:00"
    },
    {
      "sku": "SKU-00420",
      "name": "Bebidas producto 420",
      "category": "Bebidas",
      "location": "A-01",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T15:00:00"
    },
    {
      "sku": "SKU-00420",
      "name": "Bebidas producto 420",
      "category": "Bebidas",
      "location": "A-02",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T15:00:00"
    },
    {
      "sku": "SKU-00438",
      "name": "Farmacia producto 438",
      "category": "Farmacia",
      "location": "RACK-3",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T15:18:00"
    },
    {
      "sku": "SKU-00455",
      "name": "Bebidas producto 455",
      "category": "Bebidas",
      "location": "C-06",
      "available": 0,
      "daysCover": 0.0,
      "snapshotAt": "2026-04-01T15:35:00"
    }
  ],
  "auditAccuracy": [
    {
      "location": "A-02",
      "totalCounts": 40,
      "exactCounts": 5,
      "exactPct": 12.5,
      "avgAbsVariance": 2.15
    },
    {
      "location": "A-03",
      "totalCounts": 40,
      "exactCounts": 5,
      "exactPct": 12.5,
      "avgAbsVariance": 2.1
    },
    {
      "location": "B-01",
      "totalCounts": 40,
      "exactCounts": 5,
      "exactPct": 12.5,
      "avgAbsVariance": 2.1
    },
    {
      "location": "B-02",
      "totalCounts": 40,
      "exactCounts": 5,
      "exactPct": 12.5,
      "avgAbsVariance": 2.15
    },
    {
      "location": "A-01",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.25
    },
    {
      "location": "BAR-1",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.35
    },
    {
      "location": "C-05",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.25
    },
    {
      "location": "C-06",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.33
    },
    {
      "location": "RACK-2",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.33
    },
    {
      "location": "RACK-3",
      "totalCounts": 40,
      "exactCounts": 4,
      "exactPct": 10.0,
      "avgAbsVariance": 2.25
    }
  ],
  "outboxStatus": [
    {
      "status": "sent",
      "total": 1000
    },
    {
      "status": "pending",
      "total": 1000
    },
    {
      "status": "failed",
      "total": 1000
    }
  ],
  "alerts": {
    "stockoutCount": 430,
    "overstockCount": 0,
    "failedOutbox": 1000,
    "pendingOutbox": 1000,
    "incidentReceipts": 135,
    "cancelProxy": 140
  },
  "confidenceLegend": {
    "snapshot_real": "Métrica tomada directo del snapshot de inventario.",
    "audit_real": "Métrica basada en AuditCount real del snapshot.",
    "movement_damage_real": "Métrica tomada de movimientos de daño.",
    "outbox_real": "Métrica tomada de OutboxEvent.",
    "proxy_movimientos_sale": "Estimación demo a partir de movimientos reason=sale.",
    "proxy_modelo_ticket": "Modelo demo con unidades por ticket asumidas.",
    "po_vs_receipt_proxy": "Proxy de cumplimiento a partir de órdenes y recibos."
  }
} as const;
