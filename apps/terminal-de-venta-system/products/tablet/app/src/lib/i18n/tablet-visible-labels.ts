export const tabletVisibleLabels = {
  product: "PRISMA Tablet",
  role: "Terminal de venta autónoma",
  status: {
    online: "Red disponible",
    offline: "Sin red",
    localMode: "Modo local",
    pending: "pendientes",
    failed: "con error",
    loading: "cargando"
  },
  actions: {
    sell: "Vender",
    checkout: "Cobrar",
    clear: "Limpiar",
    add: "Agregar",
    search: "Buscar",
    resolveCode: "Leer código",
    viewPending: "Ver pendientes",
    newSale: "Nueva venta"
  },
  disabledReason: "Acción visual pendiente de conectar en una ronda funcional.",
  bannedVisibleTerms: ["Outbox", "Sync", "Runtime", "Lookup", "Guardrails", "SaleReturn", "amountCents", "Restock", "Stock", "Dark POS"]
} as const;
