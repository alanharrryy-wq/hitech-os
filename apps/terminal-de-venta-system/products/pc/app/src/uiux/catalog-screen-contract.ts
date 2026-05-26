export const catalogScreenContract = {
  title: "Catálogo",
  subtitle: "Revisa si tus productos están listos para venderse en tablet y PC.",
  status: "5 productos requieren revisión",
  lastUpdated: "hace 5 min",
  summaryCards: [
    {
      eyebrow: "Productos",
      title: "1,284 activos",
      tone: "ok" as const,
      lines: ["12 inactivos", "Lista principal disponible"]
    },
    {
      eyebrow: "Códigos",
      title: "2 repetidos",
      tone: "warn" as const,
      lines: ["8 sin código", "Revisión antes de enviar a tablet"]
    },
    {
      eyebrow: "Precios",
      title: "3 faltantes",
      tone: "warn" as const,
      lines: ["97% listos", "Validar antes de vender"]
    }
  ],
  recommendedAction: {
    title: "Corrige códigos repetidos antes de enviar catálogo a tablet.",
    motive: "un código repetido puede vender el producto equivocado.",
    actions: [
      { label: "Corregir códigos", href: "/integridad-barcodes", primary: true },
      { label: "Enviar cambios nuevos", href: "/sync" },
      { label: "Descargar revisión", href: "/exportables" }
    ]
  },
  tableTitle: "Productos por corregir",
  tableSubtitle: "Sólo se muestran problemas que afectan venta o sincronización.",
  columns: ["Producto", "Estado", "Qué falta", "Acción"],
  rows: [
    { Producto: "Galletas X", Estado: "Revisar", "Qué falta": "Sin código de barras", Acción: "Agregar" },
    { Producto: "Refresco Y", Estado: "Crítico", "Qué falta": "Precio faltante", Acción: "Corregir" },
    { Producto: "Agua 1L", Estado: "Revisar", "Qué falta": "Código repetido", Acción: "Resolver" },
    { Producto: "Papel Z", Estado: "Bien", "Qué falta": "Listo para vender", Acción: "Ver" }
  ],
  evidence: [
    { kind: "technical" as const,  label: "Fuente", value: "Catálogo activo, precios y códigos" },
    { kind: "technical" as const,  label: "Criterio", value: "productos activos sin datos mínimos o con código repetido" },
    { kind: "technical" as const,  label: "Confianza", value: "Alta si la revisión de datos no reporta pendientes" },
    { kind: "technical" as const,  label: "Validación", value: "Reglas disponibles en la vista de validación de catálogo" }
  ]
};
