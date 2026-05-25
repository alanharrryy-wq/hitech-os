export const systemScreenContract = {
  title: "Sistema",
  subtitle: "Revisa salud de plataforma, licencia, equipos y datos.",
  status: "Requiere revisión",
  lastUpdated: "hace 2 min",
  summaryCards: [
    {
      eyebrow: "Plataforma",
      title: "Licencia activa",
      tone: "ok" as const,
      lines: ["Funciones principales OK", "Sin bloqueo operativo"]
    },
    {
      eyebrow: "Equipos",
      title: "1 tablet atrasada",
      tone: "warn" as const,
      lines: ["PC actualizado", "Último pulso hace 12 min"]
    },
    {
      eyebrow: "Datos",
      title: "2 códigos repetidos",
      tone: "warn" as const,
      lines: ["0 errores bloqueantes", "Conviene corregir catálogo"]
    }
  ],
  recommendedAction: {
    title: "Revisar la tablet atrasada antes de cerrar operación.",
    motive: "podría faltar información reciente en PC.",
    actions: [
      { label: "Revisar sincronización", href: "/sync", primary: true },
      { label: "Ver equipos", href: "/devices" },
      { label: "Ver datos", href: "/data-quality" }
    ]
  },
  tableTitle: "Salud del sistema",
  tableSubtitle: "Áreas técnicas traducidas a acciones operativas.",
  columns: ["Área", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Área: "Licencia", Estado: "Bien", "Qué pasa": "Funciones activas", Acción: "Ver" },
    { Área: "Tablet", Estado: "Atención", "Qué pasa": "Último pulso hace 12 min", Acción: "Revisar" },
    { Área: "Datos", Estado: "Revisar", "Qué pasa": "Códigos repetidos", Acción: "Corregir" },
    { Área: "Historial", Estado: "Bien", "Qué pasa": "Eventos recientes guardados", Acción: "Ver" }
  ],
  evidence: [
    { label: "Fuente", value: "equipos, licencia, revisión de datos e historial" },
    { label: "Criterio", value: "prioridad por equipo atrasado, datos repetidos y bloqueo operativo" },
    { label: "Confianza", value: "alta cuando hay pulso reciente y eventos guardados" },
    { label: "Historial", value: "disponible en sistema y auditoría" }
  ]
};
