export const inventoryScreenContract = {
  title: "Inventario",
  subtitle: "Productos que requieren atención antes de vender, contar o comprar.",
  status: "Requiere atención",
  lastUpdated: "hace 3 min",
  summaryCards: [
    {
      eyebrow: "Atención",
      title: "4 productos críticos",
      tone: "danger" as const,
      lines: ["2 códigos repetidos", "1 conteo pendiente"]
    },
    {
      eyebrow: "Catálogo",
      title: "1,284 productos activos",
      tone: "warn" as const,
      lines: ["97% vendible", "3 productos incompletos"]
    },
    {
      eyebrow: "Sincronización",
      title: "Tablet actualizada",
      tone: "ok" as const,
      lines: ["0 cambios atorados", "Último pulso hace 3 min"]
    }
  ],
  recommendedAction: {
    title: "Revisar productos críticos primero.",
    motive: "tienen ventas recientes y quedan pocas piezas.",
    actions: [
      { label: "Revisar críticos", href: "/existencias-criticas", primary: true },
      { label: "Sugerir compra", href: "/replenishment" },
      { label: "Descargar tabla", href: "/exportables" }
    ]
  },
  tableTitle: "Productos con atención",
  tableSubtitle: "Vista operativa con problema visible y siguiente acción.",
  columns: ["Producto", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Producto: "Coca 600ml", Estado: "Crítico", "Qué pasa": "Quedan 3. Se vendieron 18", Acción: "Sugerir" },
    { Producto: "Sabritas 45g", Estado: "Revisar", "Qué pasa": "Conteo no cuadra", Acción: "Ver movimientos" },
    { Producto: "Agua 1L", Estado: "Revisar", "Qué pasa": "Código repetido", Acción: "Corregir" },
    { Producto: "Galletas X", Estado: "Pendiente", "Qué pasa": "Falta validar precio", Acción: "Revisar" },
    { Producto: "Leche 1L", Estado: "Bien", "Qué pasa": "Existencia suficiente", Acción: "Ver detalle" }
  ],
  insight: {
    title: "Riesgo de inventario",
    question: "¿Dónde puede faltar producto pronto?",
    reading: "Bebidas concentra el mayor riesgo.",
    action: "revisar reabasto sugerido.",
    bars: [
      { label: "Bebidas", value: "████████████████░░░░", level: "Alto" as const },
      { label: "Botanas", value: "████████░░░░░░░░░░░░", level: "Medio" as const },
      { label: "Abarrotes", value: "████░░░░░░░░░░░░░░░░", level: "Bajo" as const },
      { label: "Limpieza", value: "██░░░░░░░░░░░░░░░░░░", level: "Bajo" as const }
    ]
  },
  evidence: [
    { kind: "technical" as const,  label: "Fuente", value: "Existencias, movimientos recientes y conteos" },
    { kind: "technical" as const,  label: "Criterio", value: "pocas piezas, venta reciente y diferencias de conteo" },
    { kind: "technical" as const,  label: "Confianza", value: "Alta si la base principal y tablet están actualizadas" },
    { kind: "technical" as const,  label: "Historial", value: "Movimientos y conteos disponibles bajo demanda" }
  ]
};
