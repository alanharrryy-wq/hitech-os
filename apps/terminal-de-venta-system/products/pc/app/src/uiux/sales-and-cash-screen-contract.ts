export const salesAndCashScreenContract = {
  title: "Ventas y caja",
  subtitle: "Revisa ventas, cortes y diferencias antes de cerrar operación.",
  status: "Caja sana",
  lastUpdated: "hace 2 min",
  summaryCards: [
    {
      eyebrow: "Venta de hoy",
      title: "$18,420",
      tone: "ok" as const,
      lines: ["Ticket promedio: $96", "Última venta hace 4 min"]
    },
    {
      eyebrow: "Caja",
      title: "Sin diferencias",
      tone: "ok" as const,
      lines: ["Caja principal cuadrada", "Movimientos listos para revisión"]
    },
    {
      eyebrow: "Cortes",
      title: "1 abierto",
      tone: "info" as const,
      lines: ["2 cerrados", "Turno activo por cerrar"]
    }
  ],
  recommendedAction: {
    title: "Cierra el corte de la tarde cuando termine el turno.",
    motive: "no hay diferencias y la caja está lista para cierre.",
    actions: [
      { label: "Cerrar corte", href: "/cash-sessions", primary: true },
      { label: "Ver movimientos", href: "/sales-control" },
      { label: "Descargar ventas", href: "/exportables" }
    ]
  },
  tableTitle: "Cortes y cajas",
  tableSubtitle: "Cada fila dice qué pasa y qué conviene hacer antes de cerrar.",
  columns: ["Corte / caja", "Estado", "Qué pasa", "Acción"],
  rows: [
    { "Corte / caja": "Caja 1 mañana", Estado: "Cerrado", "Qué pasa": "Sin diferencia", Acción: "Ver detalle" },
    { "Corte / caja": "Caja 1 tarde", Estado: "Abierto", "Qué pasa": "Turno activo", Acción: "Cerrar" },
    { "Corte / caja": "Caja 2", Estado: "Revisar", "Qué pasa": "Diferencia de $85", Acción: "Revisar" }
  ],
  evidence: [
    { label: "Fuente", value: "Base principal de ventas y caja" },
    { label: "Cálculo", value: "ventas del día, sesiones abiertas y diferencias registradas" },
    { label: "Confianza", value: "Alta cuando la sincronización está al día" },
    { label: "Historial", value: "Disponible en la vista de cortes y auditoría" }
  ]
};
