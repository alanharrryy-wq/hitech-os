export const pcI07ValidationData = {
  "generatedAt": "2026-04-18T19:22:00",
  "policy": {
    "priceStaleDays": 14,
    "notes": [
      "Precio desactualizado = antiguedad de updatedAt mayor a 14 dias.",
      "Productos con mas de un barcode no son error automatico, pero si cola de revision.",
      "Barcodes duplicados entre productos es incidente critico. En este snapshot no se detectaron."
    ]
  },
  "totals": {
    "products_total": 5000,
    "active_products": 5000,
    "inactive_products": 0,
    "barcode_total": 6250,
    "duplicate_codes": 0,
    "active_without_barcode": 0,
    "multi_barcode_products": 1250,
    "stale_prices_14d": 3840,
    "stale_prices_7d": 5000,
    "negative_margin": 0,
    "zero_or_negative_price": 0,
    "stockout_slots": 430,
    "counts_open": 80,
    "events_pending": 1000
  },
  "headline": {
    "criticalIncidents": 0,
    "reviewQueue": 5090,
    "status": "verde_en_integridad_critica_ambar_en_politica"
  },
  "samples": {
    "duplicateCodesTop": [],
    "withoutBarcodeTop": [],
    "multiBarcodeTop": [
      {
        "id": "prd_00000",
        "sku": "SKU-00000",
        "name": "Bebidas producto 0",
        "category": "Bebidas",
        "barcode_count": 2,
        "first_code": "7501234500000",
        "last_code": "7801234500000",
        "updatedAt": "2026-04-01T08:00:00"
      },
      {
        "id": "prd_00004",
        "sku": "SKU-00004",
        "name": "Limpieza producto 4",
        "category": "Limpieza",
        "barcode_count": 2,
        "first_code": "7501234500004",
        "last_code": "7801234500004",
        "updatedAt": "2026-04-01T08:04:00"
      },
      {
        "id": "prd_00008",
        "sku": "SKU-00008",
        "name": "Farmacia producto 8",
        "category": "Farmacia",
        "barcode_count": 2,
        "first_code": "7501234500008",
        "last_code": "7801234500008",
        "updatedAt": "2026-04-01T08:08:00"
      },
      {
        "id": "prd_00012",
        "sku": "SKU-00012",
        "name": "Lácteos producto 12",
        "category": "Lácteos",
        "barcode_count": 2,
        "first_code": "7501234500012",
        "last_code": "7801234500012",
        "updatedAt": "2026-04-01T08:12:00"
      },
      {
        "id": "prd_00016",
        "sku": "SKU-00016",
        "name": "Snacks producto 16",
        "category": "Snacks",
        "barcode_count": 2,
        "first_code": "7501234500016",
        "last_code": "7801234500016",
        "updatedAt": "2026-04-01T08:16:00"
      },
      {
        "id": "prd_00020",
        "sku": "SKU-00020",
        "name": "Bebidas producto 20",
        "category": "Bebidas",
        "barcode_count": 2,
        "first_code": "7501234500020",
        "last_code": "7801234500020",
        "updatedAt": "2026-04-01T08:20:00"
      },
      {
        "id": "prd_00024",
        "sku": "SKU-00024",
        "name": "Limpieza producto 24",
        "category": "Limpieza",
        "barcode_count": 2,
        "first_code": "7501234500024",
        "last_code": "7801234500024",
        "updatedAt": "2026-04-01T08:24:00"
      },
      {
        "id": "prd_00028",
        "sku": "SKU-00028",
        "name": "Farmacia producto 28",
        "category": "Farmacia",
        "barcode_count": 2,
        "first_code": "7501234500028",
        "last_code": "7801234500028",
        "updatedAt": "2026-04-01T08:28:00"
      },
      {
        "id": "prd_00032",
        "sku": "SKU-00032",
        "name": "Lácteos producto 32",
        "category": "Lácteos",
        "barcode_count": 2,
        "first_code": "7501234500032",
        "last_code": "7801234500032",
        "updatedAt": "2026-04-01T08:32:00"
      },
      {
        "id": "prd_00036",
        "sku": "SKU-00036",
        "name": "Snacks producto 36",
        "category": "Snacks",
        "barcode_count": 2,
        "first_code": "7501234500036",
        "last_code": "7801234500036",
        "updatedAt": "2026-04-01T08:36:00"
      }
    ],
    "stalePriceTop": [
      {
        "id": "prd_00000",
        "sku": "SKU-00000",
        "name": "Bebidas producto 0",
        "category": "Bebidas",
        "priceMx": 15.0,
        "costMx": 9.45,
        "marginPct": 37.0,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:00:00"
      },
      {
        "id": "prd_00001",
        "sku": "SKU-00001",
        "name": "Snacks producto 1",
        "category": "Snacks",
        "priceMx": 16.25,
        "costMx": 10.23,
        "marginPct": 37.05,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:01:00"
      },
      {
        "id": "prd_00002",
        "sku": "SKU-00002",
        "name": "Lácteos producto 2",
        "category": "Lácteos",
        "priceMx": 17.5,
        "costMx": 11.02,
        "marginPct": 37.03,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:02:00"
      },
      {
        "id": "prd_00003",
        "sku": "SKU-00003",
        "name": "Farmacia producto 3",
        "category": "Farmacia",
        "priceMx": 18.75,
        "costMx": 11.81,
        "marginPct": 37.01,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:03:00"
      },
      {
        "id": "prd_00004",
        "sku": "SKU-00004",
        "name": "Limpieza producto 4",
        "category": "Limpieza",
        "priceMx": 20.0,
        "costMx": 12.6,
        "marginPct": 37.0,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:04:00"
      },
      {
        "id": "prd_00005",
        "sku": "SKU-00005",
        "name": "Bebidas producto 5",
        "category": "Bebidas",
        "priceMx": 21.25,
        "costMx": 13.38,
        "marginPct": 37.04,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:05:00"
      },
      {
        "id": "prd_00006",
        "sku": "SKU-00006",
        "name": "Snacks producto 6",
        "category": "Snacks",
        "priceMx": 22.5,
        "costMx": 14.17,
        "marginPct": 37.02,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:06:00"
      },
      {
        "id": "prd_00007",
        "sku": "SKU-00007",
        "name": "Lácteos producto 7",
        "category": "Lácteos",
        "priceMx": 23.75,
        "costMx": 14.96,
        "marginPct": 37.01,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:07:00"
      },
      {
        "id": "prd_00008",
        "sku": "SKU-00008",
        "name": "Farmacia producto 8",
        "category": "Farmacia",
        "priceMx": 25.0,
        "costMx": 15.75,
        "marginPct": 37.0,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:08:00"
      },
      {
        "id": "prd_00009",
        "sku": "SKU-00009",
        "name": "Limpieza producto 9",
        "category": "Limpieza",
        "priceMx": 26.25,
        "costMx": 16.53,
        "marginPct": 37.03,
        "priceAgeDays": 17,
        "updatedAt": "2026-04-01T08:09:00"
      }
    ],
    "salePressureTop": [
      {
        "sku": "SKU-00480",
        "name": "Bebidas producto 480",
        "category": "Bebidas",
        "priceMx": 60.0,
        "costMx": 37.8,
        "priceAgeDays": 17,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3360.0
      },
      {
        "sku": "SKU-02108",
        "name": "Farmacia producto 2108",
        "category": "Farmacia",
        "priceMx": 60.0,
        "costMx": 37.8,
        "priceAgeDays": 16,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3360.0
      },
      {
        "sku": "SKU-03736",
        "name": "Snacks producto 3736",
        "category": "Snacks",
        "priceMx": 60.0,
        "costMx": 37.8,
        "priceAgeDays": 15,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3360.0
      },
      {
        "sku": "SKU-01404",
        "name": "Limpieza producto 1404",
        "category": "Limpieza",
        "priceMx": 58.75,
        "costMx": 37.01,
        "priceAgeDays": 16,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3290.0
      },
      {
        "sku": "SKU-03032",
        "name": "Lácteos producto 3032",
        "category": "Lácteos",
        "priceMx": 58.75,
        "costMx": 37.01,
        "priceAgeDays": 15,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3290.0
      },
      {
        "sku": "SKU-00700",
        "name": "Bebidas producto 700",
        "category": "Bebidas",
        "priceMx": 57.5,
        "costMx": 36.22,
        "priceAgeDays": 17,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3220.0
      },
      {
        "sku": "SKU-02328",
        "name": "Farmacia producto 2328",
        "category": "Farmacia",
        "priceMx": 57.5,
        "costMx": 36.22,
        "priceAgeDays": 16,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3220.0
      },
      {
        "sku": "SKU-01624",
        "name": "Limpieza producto 1624",
        "category": "Limpieza",
        "priceMx": 56.25,
        "costMx": 35.43,
        "priceAgeDays": 16,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3150.0
      },
      {
        "sku": "SKU-03252",
        "name": "Lácteos producto 3252",
        "category": "Lácteos",
        "priceMx": 56.25,
        "costMx": 35.43,
        "priceAgeDays": 15,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3150.0
      },
      {
        "sku": "SKU-00920",
        "name": "Bebidas producto 920",
        "category": "Bebidas",
        "priceMx": 55.0,
        "costMx": 34.65,
        "priceAgeDays": 17,
        "saleEvents": 8,
        "unitsSold": 56,
        "grossSalesMx": 3080.0
      }
    ]
  }
} as const;
