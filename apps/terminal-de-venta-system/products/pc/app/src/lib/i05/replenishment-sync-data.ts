export const pcI05Data = {
  "replenishmentSummary": [
    {
      "priority": "high",
      "total": 500,
      "qty": 3250
    },
    {
      "priority": "normal",
      "total": 2000,
      "qty": 12984
    }
  ],
  "outboxStatusSummary": [
    {
      "status": "failed",
      "total": 1000
    },
    {
      "status": "pending",
      "total": 1000
    },
    {
      "status": "sent",
      "total": 1000
    }
  ],
  "avgLatencySeconds": 0.0,
  "maxLatencySeconds": 0,
  "topSignals": [
    {
      "id": "rep_02495",
      "sku": "SKU-02495",
      "name": "Bebidas producto 2495",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 62,
      "daysCover": 4.49,
      "createdAt": "2026-04-03T01:35:00"
    },
    {
      "id": "rep_02435",
      "sku": "SKU-02435",
      "name": "Bebidas producto 2435",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 22,
      "daysCover": 1.59,
      "createdAt": "2026-04-03T00:35:00"
    },
    {
      "id": "rep_02375",
      "sku": "SKU-02375",
      "name": "Bebidas producto 2375",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 52,
      "daysCover": 3.77,
      "createdAt": "2026-04-02T23:35:00"
    },
    {
      "id": "rep_02315",
      "sku": "SKU-02315",
      "name": "Bebidas producto 2315",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 12,
      "daysCover": 0.87,
      "createdAt": "2026-04-02T22:35:00"
    },
    {
      "id": "rep_02255",
      "sku": "SKU-02255",
      "name": "Bebidas producto 2255",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 42,
      "daysCover": 3.04,
      "createdAt": "2026-04-02T21:35:00"
    },
    {
      "id": "rep_02195",
      "sku": "SKU-02195",
      "name": "Bebidas producto 2195",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 2,
      "daysCover": 0.14,
      "createdAt": "2026-04-02T20:35:00"
    },
    {
      "id": "rep_02135",
      "sku": "SKU-02135",
      "name": "Bebidas producto 2135",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 32,
      "daysCover": 2.32,
      "createdAt": "2026-04-02T19:35:00"
    },
    {
      "id": "rep_02075",
      "sku": "SKU-02075",
      "name": "Bebidas producto 2075",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 62,
      "daysCover": 4.49,
      "createdAt": "2026-04-02T18:35:00"
    },
    {
      "id": "rep_02015",
      "sku": "SKU-02015",
      "name": "Bebidas producto 2015",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 22,
      "daysCover": 1.59,
      "createdAt": "2026-04-02T17:35:00"
    },
    {
      "id": "rep_01955",
      "sku": "SKU-01955",
      "name": "Bebidas producto 1955",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 52,
      "daysCover": 3.77,
      "createdAt": "2026-04-02T16:35:00"
    },
    {
      "id": "rep_01895",
      "sku": "SKU-01895",
      "name": "Bebidas producto 1895",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 12,
      "daysCover": 0.87,
      "createdAt": "2026-04-02T15:35:00"
    },
    {
      "id": "rep_01835",
      "sku": "SKU-01835",
      "name": "Bebidas producto 1835",
      "category": "Bebidas",
      "location": "C-05",
      "suggestedQty": 12,
      "priority": "high",
      "available": 42,
      "daysCover": 3.04,
      "createdAt": "2026-04-02T14:35:00"
    }
  ],
  "outboxPending": [
    {
      "id": "evt_02999",
      "topic": "product.updated",
      "aggregateId": "prd_02999",
      "status": "failed",
      "createdAt": "2026-04-03T09:59:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02999\", \"qty\": 3, \"location\": \"RACK-3\"}"
    },
    {
      "id": "evt_02997",
      "topic": "product.updated",
      "aggregateId": "prd_02997",
      "status": "pending",
      "createdAt": "2026-04-03T09:57:00",
      "sentAt": "2026-04-03T09:57:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02997\", \"qty\": 1, \"location\": \"BAR-1\"}"
    },
    {
      "id": "evt_02996",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02996",
      "status": "failed",
      "createdAt": "2026-04-03T09:56:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02996\", \"qty\": 9, \"location\": \"C-06\"}"
    },
    {
      "id": "evt_02994",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02994",
      "status": "pending",
      "createdAt": "2026-04-03T09:54:00",
      "sentAt": "2026-04-03T09:54:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02994\", \"qty\": 7, \"location\": \"B-02\"}"
    },
    {
      "id": "evt_02993",
      "topic": "product.updated",
      "aggregateId": "prd_02993",
      "status": "failed",
      "createdAt": "2026-04-03T09:53:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02993\", \"qty\": 6, \"location\": \"B-01\"}"
    },
    {
      "id": "evt_02991",
      "topic": "product.updated",
      "aggregateId": "prd_02991",
      "status": "pending",
      "createdAt": "2026-04-03T09:51:00",
      "sentAt": "2026-04-03T09:51:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02991\", \"qty\": 4, \"location\": \"A-02\"}"
    },
    {
      "id": "evt_02990",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02990",
      "status": "failed",
      "createdAt": "2026-04-03T09:50:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02990\", \"qty\": 3, \"location\": \"A-01\"}"
    },
    {
      "id": "evt_02988",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02988",
      "status": "pending",
      "createdAt": "2026-04-03T09:48:00",
      "sentAt": "2026-04-03T09:48:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02988\", \"qty\": 1, \"location\": \"RACK-2\"}"
    },
    {
      "id": "evt_02987",
      "topic": "product.updated",
      "aggregateId": "prd_02987",
      "status": "failed",
      "createdAt": "2026-04-03T09:47:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02987\", \"qty\": 9, \"location\": \"BAR-1\"}"
    },
    {
      "id": "evt_02985",
      "topic": "product.updated",
      "aggregateId": "prd_02985",
      "status": "pending",
      "createdAt": "2026-04-03T09:45:00",
      "sentAt": "2026-04-03T09:45:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02985\", \"qty\": 7, \"location\": \"C-05\"}"
    },
    {
      "id": "evt_02984",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02984",
      "status": "failed",
      "createdAt": "2026-04-03T09:44:00",
      "sentAt": null,
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02984\", \"qty\": 6, \"location\": \"B-02\"}"
    },
    {
      "id": "evt_02982",
      "topic": "stock.adjusted",
      "aggregateId": "prd_02982",
      "status": "pending",
      "createdAt": "2026-04-03T09:42:00",
      "sentAt": "2026-04-03T09:42:00",
      "latencySeconds": 0,
      "payloadJson": "{\"sku\": \"SKU-02982\", \"qty\": 4, \"location\": \"A-03\"}"
    }
  ],
  "riskSignals": [
    {
      "sku": "SKU-00070",
      "name": "Bebidas producto 70",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-00490",
      "name": "Bebidas producto 490",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-00910",
      "name": "Bebidas producto 910",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-01330",
      "name": "Bebidas producto 1330",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-01750",
      "name": "Bebidas producto 1750",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-02170",
      "name": "Bebidas producto 2170",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 11,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-00140",
      "name": "Bebidas producto 140",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-00560",
      "name": "Bebidas producto 560",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-00980",
      "name": "Bebidas producto 980",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-01400",
      "name": "Bebidas producto 1400",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-01820",
      "name": "Bebidas producto 1820",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    },
    {
      "sku": "SKU-02240",
      "name": "Bebidas producto 2240",
      "category": "Bebidas",
      "location": "A-01",
      "priority": "high",
      "suggestedQty": 9,
      "available": 0,
      "daysCover": 0.0,
      "riskBand": "quiebre"
    }
  ],
  "sharedEvents": [
    "catalog.updated",
    "stock.adjusted",
    "stock.received",
    "purchase_order.created",
    "replenishment.requested",
    "audit.completed",
    "sync.started",
    "sync.succeeded",
    "sync.failed",
    "sync.conflict_detected",
    "outbox.enqueued",
    "outbox.dispatched"
  ]
} as const;
