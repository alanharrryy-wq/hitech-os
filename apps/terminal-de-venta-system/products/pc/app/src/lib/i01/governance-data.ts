export const i01GovernanceData = {
  product: "Panel administrativo de inventario",
  twin: "Terminal de venta",
  principles: [
    "Cada iteración suma y no reemplaza",
    "PC evoluciona como frente activo",
    "Los cambios a shared-kernel se tratan como gemelos",
    "El glosario visible privilegia es-MX claro"
  ],
  sharedSurfaces: [
    "shared/twin-kernel/*",
    "shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json",
    "eventos compartidos de sincronización",
    "glosario visible cuando afecte identidad espejo"
  ],
  localPcSurfaces: [
    "catalog",
    "stock",
    "counts",
    "purchasing",
    "receiving",
    "replenishment",
    "audit",
    "sync"
  ],
  kpis: [
    "Ventas netas",
    "Número de tickets",
    "Ticket promedio",
    "Top SKUs",
    "Quiebres de stock",
    "Exactitud de inventario",
    "Merma",
    "Cancelaciones",
    "Fill rate"
  ]
} as const;
