export const syncScreenContract = {
  title: "Sincronización",
  subtitle: "Revisa si PC, tablet y móvil tienen la misma información.",
  status: "Tablet atrasada",
  lastUpdated: "hace 1 min",
  summaryCards: [
    {
      eyebrow: "Equipos",
      title: "1 tablet atrasada",
      tone: "warn" as const,
      lines: ["PC actualizado", "móvil con avisos pendientes"]
    },
    {
      eyebrow: "Cambios",
      title: "3 cambios pendientes",
      tone: "info" as const,
      lines: ["último envío hace 12 min", "confirmación pendiente"]
    },
    {
      eyebrow: "Conflictos",
      title: "0 bloqueantes",
      tone: "ok" as const,
      lines: ["1 por revisar", "operación disponible"]
    }
  ],
  recommendedAction: {
    title: "Enviar cambios nuevos a Tablet caja 1.",
    motive: "la tablet no ha confirmado el catálogo más reciente.",
    actions: [
      { label: "Enviar cambios", href: "/sync", primary: true },
      { label: "Reintentar sincronización", href: "/sync-operativo" },
      { label: "Ver pendientes", href: "/outbox-operativo" }
    ]
  },
  tableTitle: "Equipos y cambios",
  tableSubtitle: "Estado operativo entre PC, tablet y móvil sin lenguaje técnico en primera lectura.",
  columns: ["Equipo", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Equipo: "PC", Estado: "Bien", "Qué pasa": "Base principal actualizada", Acción: "Ver historial" },
    { Equipo: "Tablet caja 1", Estado: "Atrasada", "Qué pasa": "Sin confirmar hace 12 min", Acción: "Enviar" },
    { Equipo: "Móvil dueño", Estado: "Pendiente", "Qué pasa": "3 alertas por entregar", Acción: "Reintentar" }
  ],
  insight: {
    title: "Vida de la sincronización",
    question: "¿Dónde se atoró la actualización?",
    reading: "La tablet recibió datos, pero falta confirmación.",
    action: "reintentar confirmación.",
    bars: [
      { label: "Preparado", value: "██████████", level: "Bajo" as const },
      { label: "Enviado", value: "██████████", level: "Bajo" as const },
      { label: "Recibido", value: "██████████", level: "Bajo" as const },
      { label: "Confirmado", value: "███░░░░░░░", level: "Medio" as const }
    ]
  },
  evidence: [
    { label: "Fuente", value: "estado de equipos, cambios por enviar y confirmaciones recientes" },
    { label: "Criterio", value: "último pulso, cambios nuevos y pendientes de confirmación" },
    { label: "Riesgo", value: "puede faltar información reciente en tablet si no confirma" },
    { label: "Historial", value: "detalle disponible en sincronización y tablet" }
  ]
};
