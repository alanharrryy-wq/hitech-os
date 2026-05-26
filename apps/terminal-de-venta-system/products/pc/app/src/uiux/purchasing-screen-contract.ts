export const purchasingScreenContract = {
  title: "Compras",
  subtitle: "Decide qué pedir, qué recibir y qué cerrar.",
  status: "Hay pedidos pendientes",
  lastUpdated: "hace 4 min",
  summaryCards: [
    {
      eyebrow: "Pedidos",
      title: "3 abiertos",
      tone: "warn" as const,
      lines: ["1 parcial", "2 listos para revisar"]
    },
    {
      eyebrow: "Recepciones",
      title: "2 pendientes",
      tone: "warn" as const,
      lines: ["1 con diferencia", "1 lista para registrar"]
    },
    {
      eyebrow: "Reabasto",
      title: "8 productos sugeridos",
      tone: "info" as const,
      lines: ["$4,200 estimado", "Bebidas concentra prioridad"]
    }
  ],
  recommendedAction: {
    title: "Registrar recepción de Bebidas MX.",
    motive: "el pedido ya está marcado como enviado y contiene productos críticos.",
    actions: [
      { label: "Registrar recepción", href: "/receiving", primary: true },
      { label: "Ver pedido", href: "/ordenes-compra" },
      { label: "Ver diferencias", href: "/incidencias-recepcion" }
    ]
  },
  tableTitle: "Compras por atender",
  tableSubtitle: "Pedidos, recepciones y reabasto ordenados por impacto operativo.",
  columns: ["Pedido", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Pedido: "Pedido 102", Estado: "Enviado", "Qué pasa": "Listo para recibir", Acción: "Recibir" },
    { Pedido: "Pedido 103", Estado: "Parcial", "Qué pasa": "Faltaron 4 piezas", Acción: "Revisar" },
    { Pedido: "Sugerido", Estado: "Bien", "Qué pasa": "Reabasto recomendado", Acción: "Crear" }
  ],
  evidence: [
    { kind: "technical" as const,  label: "Fuente", value: "Pedidos, recepciones y señal de reabasto" },
    { kind: "technical" as const,  label: "Criterio", value: "prioridad por piezas críticas, pedido enviado y diferencia pendiente" },
    { kind: "technical" as const,  label: "Confianza", value: "alta cuando existe pedido y recepción relacionada" },
    { kind: "technical" as const,  label: "Historial", value: "disponible en compras y recepciones" }
  ]
};
