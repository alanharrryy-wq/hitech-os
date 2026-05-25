export const reportsScreenContract = {
  title: "Reportes",
  subtitle: "Descarga información clara para revisar, compartir o auditar.",
  status: "Reportes listos",
  lastUpdated: "hace 8 min",
  summaryCards: [
    {
      eyebrow: "Ventas",
      title: "Hoy listo",
      tone: "ok" as const,
      lines: ["CSV y PDF preparados", "Corte listo para revisar"]
    },
    {
      eyebrow: "Inventario",
      title: "Críticos listo",
      tone: "info" as const,
      lines: ["Tabla de productos bajos", "Lista útil para pedidos"]
    },
    {
      eyebrow: "Auditoría",
      title: "Cambios listo",
      tone: "ok" as const,
      lines: ["Responsables y fechas", "Exportable para revisión"]
    }
  ],
  recommendedAction: {
    title: "Descargar resumen de ventas del día.",
    motive: "el corte está listo y no hay diferencias pendientes.",
    actions: [
      { label: "Descargar ventas", href: "/exportables", primary: true },
      { label: "Ver antes", href: "/metricas-dia" },
      { label: "Copiar resumen", href: "/contratos-reporte" }
    ]
  },
  tableTitle: "Reportes disponibles",
  tableSubtitle: "Información lista para revisar, compartir o guardar.",
  columns: ["Reporte", "Para qué sirve", "Formato", "Acción"],
  rows: [
    { Reporte: "Ventas del día", "Para qué sirve": "Corte y revisión", Formato: "CSV / PDF", Acción: "Descargar" },
    { Reporte: "Inventario crítico", "Para qué sirve": "Preparar compra", Formato: "CSV", Acción: "Descargar" },
    { Reporte: "Auditoría", "Para qué sirve": "Cambios y responsables", Formato: "CSV", Acción: "Descargar" },
    { Reporte: "Proveedores", "Para qué sirve": "Pagos, pedidos y recepción", Formato: "CSV", Acción: "Descargar" }
  ],
  evidence: [
    { label: "Fuente", value: "ventas, inventario, compras y historial" },
    { label: "Criterio", value: "reportes visibles sólo cuando tienen propósito operativo" },
    { label: "Confianza", value: "alta cuando corte, tabla y filtros están listos" },
    { label: "Origen", value: "exportables y métricas internas" }
  ]
};
