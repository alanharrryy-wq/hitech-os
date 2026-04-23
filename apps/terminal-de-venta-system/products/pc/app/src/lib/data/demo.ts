import { pcMessages } from "@/lib/i18n/messages/es";

export const categoryMix = [
  ["Validación de barcodes", 18],
  ["Conteos urgentes", 7],
  ["Recepciones abiertas", 4],
  ["Sync pendiente", 6],
  ["Precio desfasado", 9]
] as const;

export const lowStock = [
  { sku: "CCZ-600", name: "Coca-Cola Zero 600ml", location: "A-01", days: 0.4, status: pcMessages.statuses.critical },
  { sku: "PAN-RBN", name: "Pan blanco rebanado", location: "B-03", days: 0.8, status: pcMessages.statuses.critical },
  { sku: "GAT-ATN", name: "Galleta avena 6p", location: "C-02", days: 1.2, status: pcMessages.statuses.risk },
  { sku: "LEC-DES", name: "Leche deslactosada 1L", location: "F-07", days: 1.0, status: pcMessages.statuses.risk },
  { sku: "JAB-ZOT", name: "Jabón Zote rosa", location: "H-01", days: 0.6, status: pcMessages.statuses.critical }
];

export const openOrders = [
  { po: "CCR-600", supplier: "Coca-Cola regular 600ml", lines: 468, eta: "$44,993", status: "$1,739" },
  { po: "ANT-244", supplier: "Antartto", lines: 244, eta: "$16,655", status: "$259" },
  { po: "FNT-221", supplier: "Frituras surtidas mix", lines: 221, eta: "$75,065", status: "$990" },
  { po: "LTE-261", supplier: "Lenteja instant 1L", lines: 261, eta: "$21,955", status: "$901" }
];

export const pendingSync = [
  { id: "evt_pc_001", topic: "stock.adjusted", age: "00:02:14", status: pcMessages.statuses.pending },
  { id: "evt_pc_002", topic: "catalog.updated", age: "00:04:45", status: pcMessages.statuses.pending },
  { id: "evt_pc_003", topic: "purchase_order.created", age: "00:08:11", status: pcMessages.statuses.sent },
  { id: "evt_pc_004", topic: "sync.failed", age: "00:13:54", status: pcMessages.statuses.failed }
];

export const signalPills = [
  "Inventario bajo (22)",
  "Productos caducos (5+)",
  "Ventas bajas"
] as const;

export const summaryCards = [
  {
    label: "SKUs en inventario",
    value: "542",
    note: "Catálogo activo con trazabilidad al día.",
    icon: "◈",
    details: [
      { label: "Sin barcode", value: "08" },
      { label: "Duplicados", value: "03" }
    ]
  },
  {
    label: "Stock bajo",
    value: "12",
    note: "2 SKUs ya están debajo de su mínimo duro.",
    icon: "△",
    details: [
      { label: "En riesgo", value: "07" },
      { label: "Quiebre hoy", value: "02" }
    ]
  },
  {
    label: "Ventas del día",
    value: "$3,871.40",
    note: "+ 2.6% contra la misma hora de ayer.",
    icon: "✦",
    details: [
      { label: "Tickets", value: "124" },
      { label: "Promedio", value: "$31.22" }
    ]
  }
] as const;

export const actionCards = [
  {
    title: "Abrir tablero de quiebres",
    description: "Concentra productos críticos, alerta de cobertura y demanda perdida estimada."
  },
  {
    title: "Entrar a auditoría rápida",
    description: "Revisa ajustes pendientes, diferencias físicas y conteos con mayor ruido."
  },
  {
    title: "Monitorear sincronización",
    description: "Verifica outbox, latencia y eventos que ya empezaron a hacer fila."
  }
] as const;

export const alertStrip = {
  title: "2 SKUs ya están en zona roja",
  subtitle: "Conviene atacar Coca-Cola Zero 600ml y pan blanco antes del siguiente pico de venta."
} as const;
