export const pcMessages = {
  metadata: {
    title: "Panel administrativo de inventario 6.1.1",
    description: "Base operativa saneada para inventario, catálogo y control operativo en PC."
  },
  productName: "Panel administrativo de inventario",
  shell: {
    brand: "PRISMA",
    subtitle: "Inventario, SKUs, compras, recepción, auditoría y sincronización con la terminal gemela.",
    footer: "Gemela: terminal de venta. Dominio: inventario y control operativo.",
    home: "Visión general",
    twinStatus: "Tablet conectada",
    lastSincronización: "sin sincronización reciente",
    lastSync: "sin sincronización reciente",
    searchPlaceholder: "Buscar SKU, ID o escanear código",
    sincronizaciónChip: "Revisar sincronización",
    syncChip: "Revisar sincronización",
    userChip: "Administrador"
  },
  home: {
    kicker: "tablero operativo",
    title: "Visual del inventario",
    subtitle: "Qué puede hacer PRISMA por venta, inventario, compras, reabasto, supervisión y crecimiento multi-sucursal.",
    criticalStockTitle: "Productos con existencias bajas",
    criticalStockSubtitle: "Lo que ya está pidiendo reabasto o conteo físico antes de volverse quiebre.",
    openOrdersTitle: "Top productos vendidos",
    openOrdersSubtitle: "Lectura rápida del catálogo que sí está empujando venta y margen.",
    categoryMixTitle: "Señales operativas",
    categoryMixSubtitle: "Atajos para moverse por las áreas con más fricción del turno.",
    pendingSincronizaciónTitle: "Sincronización pendiente",
    pendingSincronizaciónSubtitle: "Eventos listos o pendientes para sincronizar con la terminal de venta.",
    lowStockColumns: ["SKU", "Producto", "Ubicación", "Días", "Estado"],
    openOrdersColumns: ["SKU", "Producto", "Unidades", "Ingreso", "Margen"],
    pendingSincronizaciónColumns: ["Evento", "Tipo", "Antigüedad", "Estado"]
  },
  pages: {
    counts: {
      title: "Conteos físicos",
      subtitle: "Ciclos de conteo y conciliación con sistema.",
      bullets: ["conteos cíclicos", "variaciones", "exactitud de inventario", "pendientes"]
    },
    purchasing: {
      title: "Compras",
      subtitle: "Órdenes de compra y cumplimiento por proveedor.",
      bullets: ["órdenes abiertas", "fill rate", "tiempo de entrega", "pendientes de surtido"]
    },
    stock: {
      title: "Existencias",
      subtitle: "Foto operativa de existencias, cobertura y quiebres.",
      bullets: ["existencias actuales", "días de inventario", "quiebres", "sobreinventario"]
    },
    sincronización: {
      title: "Sincronización",
      subtitle: "Intercambio de eventos con la terminal de venta.",
      bullets: ["bandeja de salida", "reintentos", "conflictos", "confirmación"]
    }
  },
  statuses: {
    critical: "crítico",
    risk: "en riesgo",
    ordered: "solicitada",
    partial: "parcial",
    pending: "pendiente",
    sent: "enviado",
    failed: "fallido"
  }
} as const;
