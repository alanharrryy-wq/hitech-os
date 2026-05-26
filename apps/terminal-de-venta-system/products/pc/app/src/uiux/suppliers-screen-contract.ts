export const suppliersScreenContract = {
  title: "Proveedores",
  subtitle: "Atiende compras, recepciones, pagos e historial por proveedor.",
  status: "Hay acciones pendientes",
  lastUpdated: "hace 3 min",
  summaryCards: [
    {
      eyebrow: "Recomendado",
      title: "Bebidas MX",
      tone: "ok" as const,
      lines: ["Cubre 8 productos bajos", "Entrega reciente completa"]
    },
    {
      eyebrow: "Pendientes",
      title: "2 recepciones",
      tone: "warn" as const,
      lines: ["1 pedido parcial", "1 recepción con diferencia"]
    },
    {
      eyebrow: "Pagos",
      title: "1 vence mañana",
      tone: "warn" as const,
      lines: ["$2,850 próximos", "requiere confirmación"]
    }
  ],
  recommendedAction: {
    title: "Crear pedido de reabasto con Bebidas MX.",
    motive: "cubre 8 productos bajos y tuvo entregas completas recientes.",
    actions: [
      { label: "Crear pedido", href: "/proveedores", primary: true },
      { label: "Probar sugerencia", href: "/proveedores" },
      { label: "Comparar proveedor", href: "/proveedores" }
    ]
  },
  tableTitle: "Proveedores por atender",
  tableSubtitle: "Prioridad humana para compra, recepción y pago.",
  columns: ["Proveedor", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Proveedor: "Bebidas MX", Estado: "Bien", "Qué pasa": "Cubre productos bajos", Acción: "Crear pedido" },
    { Proveedor: "Abarrotes Norte", Estado: "Revisar", "Qué pasa": "Recepción con diferencia", Acción: "Ver recepción" },
    { Proveedor: "Dulces Sur", Estado: "Pendiente", "Qué pasa": "Pago vence mañana", Acción: "Ver pago" }
  ],
  evidence: [
    { kind: "technical" as const,  label: "Fuente", value: "proveedores, pedidos, recepciones y cuentas por pagar" },
    { kind: "technical" as const,  label: "Criterio", value: "cobertura de productos bajos, cumplimiento reciente y vencimientos" },
    { kind: "technical" as const,  label: "Confirmación", value: "acciones reales deben revisarse antes de guardar" },
    { kind: "governance" as const,  label: "Historial", value: "eventos y responsables disponibles en auditoría" }
  ]
};
