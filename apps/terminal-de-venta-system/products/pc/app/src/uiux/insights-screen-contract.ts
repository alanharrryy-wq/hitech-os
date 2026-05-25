export const insightsScreenContract = {
  title: "Análisis",
  subtitle: "Encuentra patrones que explican ventas, inventario, compras y sincronización.",
  status: "Datos suficientes",
  lastUpdated: "hace 6 min",
  summaryCards: [
    {
      eyebrow: "Riesgo principal",
      title: "Inventario",
      tone: "warn" as const,
      lines: ["4 productos críticos", "Bebidas concentra presión"]
    },
    {
      eyebrow: "Área con presión",
      title: "Bebidas",
      tone: "warn" as const,
      lines: ["62% del riesgo", "Venta reciente alta"]
    },
    {
      eyebrow: "Confianza",
      title: "Alta",
      tone: "ok" as const,
      lines: ["Datos recientes", "Lectura consistente"]
    }
  ],
  recommendedAction: {
    title: "Revisar riesgo de inventario antes de comprar.",
    motive: "las gráficas detectan presión en bebidas y pedidos pendientes.",
    actions: [
      { label: "Ver riesgo", href: "/prisma-insights", primary: true },
      { label: "Ir a reabasto", href: "/replenishment" },
      { label: "Descargar análisis", href: "/exportables" }
    ]
  },
  tableTitle: "Gráficas operativas",
  tableSubtitle: "Cada gráfica responde una pregunta y debe llevar lectura humana.",
  columns: ["Gráfica", "Qué responde", "Acción"],
  rows: [
    { Gráfica: "Riesgo de inventario", "Qué responde": "Dónde puede faltar producto", Acción: "Ver riesgo" },
    { Gráfica: "Flujo causa acción", "Qué responde": "Qué evento provocó la recomendación", Acción: "Revisar causa" },
    { Gráfica: "Mapa de dependencias", "Qué responde": "Qué módulo afecta a otro", Acción: "Ver relación" },
    { Gráfica: "Historial de decisiones", "Qué responde": "Qué decidió PRISMA y cuándo", Acción: "Ver historial" },
    { Gráfica: "Impacto en dinero", "Qué responde": "Qué cambió en ventas, compras o caja", Acción: "Ver impacto" }
  ],
  insight: {
    title: "Riesgo de inventario",
    question: "Pregunta: ¿Dónde puede faltar producto?",
    reading: "Lectura rápida: Bebidas concentra riesgo alto por venta reciente.",
    action: "revisar compra sugerida.",
    bars: [
      { label: "Bebidas", value: "████████████████░░░░", level: "Alto" as const },
      { label: "Botanas", value: "████████░░░░░░░░░░░░", level: "Medio" as const },
      { label: "Abarrotes", value: "████░░░░░░░░░░░░░░░░", level: "Bajo" as const }
    ]
  },
  evidence: [
    { label: "Fuente", value: "ventas, inventario, compras y sincronización" },
    { label: "Criterio", value: "riesgo por venta reciente, disponibilidad y pedidos pendientes" },
    { label: "Confianza", value: "alta cuando los datos son recientes y consistentes" },
    { label: "Fórmula", value: "ponderación operativa con severidad, frescura y disponibilidad" }
  ]
};
