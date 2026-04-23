export const procurementStats = {
  "ordenesAbiertas": 200,
  "proveedoresActivos": 5,
  "recepcionesConIncidencia": 135,
  "lineasPlaneacion": 12000,
  "topProveedor": "Bebidas del Centro"
} as const;

export const purchasePulse = [
  {
    "folio": "PO-2599",
    "supplier": "Farmacia Barrial",
    "status": "ordered",
    "eta_days": 5
  },
  {
    "folio": "PO-2597",
    "supplier": "Lácteos del Norte",
    "status": "partial",
    "eta_days": 3
  },
  {
    "folio": "PO-2596",
    "supplier": "Snacks MX",
    "status": "ordered",
    "eta_days": 2
  },
  {
    "folio": "PO-2594",
    "supplier": "Farmacia Barrial",
    "status": "partial",
    "eta_days": 5
  },
  {
    "folio": "PO-2593",
    "supplier": "Limpieza Uno",
    "status": "ordered",
    "eta_days": 4
  },
  {
    "folio": "PO-2591",
    "supplier": "Snacks MX",
    "status": "partial",
    "eta_days": 2
  },
  {
    "folio": "PO-2590",
    "supplier": "Bebidas del Centro",
    "status": "ordered",
    "eta_days": 1
  },
  {
    "folio": "PO-2588",
    "supplier": "Limpieza Uno",
    "status": "partial",
    "eta_days": 4
  }
] as const;

export const receivingIncidents = [
  {
    "purchaseId": "po_0536",
    "supplier": "Snacks MX",
    "receivedAt": "2026-06-30T16:00:00",
    "lines": 17
  },
  {
    "purchaseId": "po_0532",
    "supplier": "Lácteos del Norte",
    "receivedAt": "2026-06-30T00:00:00",
    "lines": 13
  },
  {
    "purchaseId": "po_0528",
    "supplier": "Limpieza Uno",
    "receivedAt": "2026-06-29T08:00:00",
    "lines": 9
  },
  {
    "purchaseId": "po_0524",
    "supplier": "Farmacia Barrial",
    "receivedAt": "2026-06-28T16:00:00",
    "lines": 5
  },
  {
    "purchaseId": "po_0520",
    "supplier": "Bebidas del Centro",
    "receivedAt": "2026-06-28T00:00:00",
    "lines": 19
  },
  {
    "purchaseId": "po_0516",
    "supplier": "Snacks MX",
    "receivedAt": "2026-06-27T08:00:00",
    "lines": 15
  },
  {
    "purchaseId": "po_0512",
    "supplier": "Lácteos del Norte",
    "receivedAt": "2026-06-26T16:00:00",
    "lines": 11
  },
  {
    "purchaseId": "po_0508",
    "supplier": "Limpieza Uno",
    "receivedAt": "2026-06-26T00:00:00",
    "lines": 7
  }
] as const;

export const supplierHeat = [
  {
    "supplier": "Bebidas del Centro",
    "total_orders": 140,
    "partial_count": 46,
    "received_count": 47
  },
  {
    "supplier": "Farmacia Barrial",
    "total_orders": 140,
    "partial_count": 47,
    "received_count": 46
  },
  {
    "supplier": "Limpieza Uno",
    "total_orders": 140,
    "partial_count": 46,
    "received_count": 47
  },
  {
    "supplier": "Lácteos del Norte",
    "total_orders": 140,
    "partial_count": 47,
    "received_count": 47
  },
  {
    "supplier": "Snacks MX",
    "total_orders": 140,
    "partial_count": 47,
    "received_count": 46
  }
] as const;
