export const purchasingScreenContract = {
  title: "Compras",
  subtitle: "Centro de compras: pedidos, recepciones, diferencias, reabasto y forecast en una sola línea operativa.",
  status: "Base de compras limpia",
  lastUpdated: "Lectura actual",
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
    { kind: "technical" as const, label: "Fuente", value: "Pedidos, recepciones y señal de reabasto" },
    { kind: "technical" as const, label: "Criterio", value: "prioridad por piezas críticas, pedido enviado y diferencia pendiente" },
    { kind: "technical" as const, label: "Confianza", value: "alta cuando existe pedido y recepción relacionada" },
    { kind: "technical" as const, label: "Historial", value: "disponible en compras y recepciones" }
  ]
};

export const purchasingRouteContracts = {
  "/purchasing": purchasingScreenContract,
  "/ordenes-compra": {
    title: "Órdenes de compra",
    subtitle: "Pedidos abiertos, enviados y parciales sin mezclarse con recepción ni reabasto.",
    status: "Pedidos por revisar",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Abiertos", title: "3 pedidos", tone: "warn" as const, lines: ["2 listos para seguimiento", "1 parcial"] },
      { eyebrow: "Enviado", title: "1 listo para recibir", tone: "info" as const, lines: ["Bebidas MX", "requiere recepción"] },
      { eyebrow: "Impacto", title: "$4,200 estimado", tone: "info" as const, lines: ["prioridad por productos críticos", "sin acción destructiva"] }
    ],
    recommendedAction: {
      title: "Revisar pedido enviado antes de registrar recepción.",
      motive: "la orden debe conservar trazabilidad antes de tocar inventario.",
      actions: [
        { label: "Abrir recepción", href: "/receiving", primary: true },
        { label: "Ver diferencias", href: "/incidencias-recepcion" },
        { label: "Ver reabasto", href: "/replenishment" }
      ]
    },
    tableTitle: "Órdenes por atender",
    tableSubtitle: "Estado visible de pedidos antes de recepción.",
    columns: ["Pedido", "Proveedor", "Estado", "Siguiente paso"],
    rows: [
      { Pedido: "Pedido 102", Proveedor: "Bebidas MX", Estado: "Enviado", "Siguiente paso": "Registrar recepción" },
      { Pedido: "Pedido 103", Proveedor: "Abarrotes Norte", Estado: "Parcial", "Siguiente paso": "Revisar faltantes" },
      { Pedido: "Sugerido", Proveedor: "Reabasto automático", Estado: "Borrador", "Siguiente paso": "Validar forecast" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/ordenes-compra" },
      { kind: "technical" as const, label: "Scope", value: "órdenes de compra, sin mutar recepción" },
      { kind: "technical" as const, label: "Contrato", value: "purchasing route contract aislado" }
    ]
  },
  "/receiving": {
    title: "Recepción",
    subtitle: "Recepciones pendientes y confirmación operativa antes de inventario.",
    status: "Recepción pendiente",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Cola", title: "2 recepciones", tone: "warn" as const, lines: ["1 con diferencia", "1 lista para registrar"] },
      { eyebrow: "Inventario", title: "Movimiento previsto", tone: "info" as const, lines: ["se confirma al recibir", "no se simula cierre"] },
      { eyebrow: "Riesgo", title: "Diferencia visible", tone: "warn" as const, lines: ["requiere motivo", "mantiene auditoría"] }
    ],
    recommendedAction: {
      title: "Confirmar recepción con cantidades visibles.",
      motive: "la recepción puede crear movimiento de inventario y debe ser trazable.",
      actions: [
        { label: "Recibir proveedor", href: "/recepcion-proveedor", primary: true },
        { label: "Ver orden", href: "/ordenes-compra" },
        { label: "Ver diferencias", href: "/incidencias-recepcion" }
      ]
    },
    tableTitle: "Recepciones por confirmar",
    tableSubtitle: "Cada recepción declara estado, diferencia y acción segura.",
    columns: ["Recepción", "Proveedor", "Estado", "Acción"],
    rows: [
      { Recepción: "REC-102", Proveedor: "Bebidas MX", Estado: "Lista", Acción: "Confirmar" },
      { Recepción: "REC-103", Proveedor: "Abarrotes Norte", Estado: "Con diferencia", Acción: "Revisar" },
      { Recepción: "REC-104", Proveedor: "Lácteos Centro", Estado: "Esperada", Acción: "Esperar llegada" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/receiving" },
      { kind: "technical" as const, label: "Scope", value: "recepción operativa" },
      { kind: "technical" as const, label: "Contrato", value: "no sustituye diferencias ni forecast" }
    ]
  },
  "/recepcion-proveedor": {
    title: "Recibir proveedor",
    subtitle: "Pantalla enfocada a registrar llegada de proveedor sin disfrazarse de /receiving.",
    status: "Lista para captura",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Proveedor", title: "Bebidas MX", tone: "info" as const, lines: ["orden enviada", "folio pendiente"] },
      { eyebrow: "Captura", title: "Cantidades visibles", tone: "warn" as const, lines: ["confirmar líneas", "motivo si hay diferencia"] },
      { eyebrow: "Auditoría", title: "Requiere trazabilidad", tone: "info" as const, lines: ["actor visible", "movimiento previsto"] }
    ],
    recommendedAction: {
      title: "Capturar cantidades recibidas por línea.",
      motive: "esta subpantalla es de ejecución, no sólo consulta de recepción.",
      actions: [
        { label: "Ver diferencias", href: "/incidencias-recepcion", primary: true },
        { label: "Ver orden", href: "/ordenes-compra" },
        { label: "Volver a recepción", href: "/receiving" }
      ]
    },
    tableTitle: "Líneas de proveedor",
    tableSubtitle: "Base limpia para captura visual posterior.",
    columns: ["Producto", "Pedido", "Recibido", "Estado"],
    rows: [
      { Producto: "Agua mineral", Pedido: 24, Recibido: 24, Estado: "Completo" },
      { Producto: "Refresco lata", Pedido: 18, Recibido: 14, Estado: "Diferencia" },
      { Producto: "Jugo familiar", Pedido: 12, Recibido: 12, Estado: "Completo" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/recepcion-proveedor" },
      { kind: "technical" as const, label: "Corrección", value: "currentPath propio, no alias /receiving" },
      { kind: "technical" as const, label: "Scope", value: "subpantalla de captura" }
    ]
  },
  "/replenishment": {
    title: "Reabasto",
    subtitle: "Señales y sugeridos de compra sin confundirse con forecast ni órdenes.",
    status: "Reabasto sugerido",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Sugeridos", title: "8 productos", tone: "info" as const, lines: ["bebidas al frente", "prioridad por mínimos"] },
      { eyebrow: "Inventario", title: "2 críticos", tone: "warn" as const, lines: ["necesitan pedido", "sin cierre automático"] },
      { eyebrow: "Presupuesto", title: "$4,200", tone: "info" as const, lines: ["estimado", "validar proveedor"] }
    ],
    recommendedAction: {
      title: "Convertir sugerido en orden revisable.",
      motive: "reabasto recomienda, compras decide y recepción confirma.",
      actions: [
        { label: "Crear orden", href: "/ordenes-compra", primary: true },
        { label: "Ver señal", href: "/senal-reabasto" },
        { label: "Ver forecast", href: "/forecast-basico" }
      ]
    },
    tableTitle: "Sugeridos de reabasto",
    tableSubtitle: "Productos que podrían convertirse en orden.",
    columns: ["SKU", "Producto", "Prioridad", "Sugerido"],
    rows: [
      { SKU: "BEB-001", Producto: "Agua mineral", Prioridad: "Alta", Sugerido: 24 },
      { SKU: "BEB-014", Producto: "Refresco lata", Prioridad: "Media", Sugerido: 18 },
      { SKU: "ABA-220", Producto: "Galleta familiar", Prioridad: "Baja", Sugerido: 8 }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/replenishment" },
      { kind: "technical" as const, label: "Scope", value: "sugerido de reabasto" },
      { kind: "technical" as const, label: "Contrato", value: "no registra recepción" }
    ]
  },
  "/incidencias-recepcion": {
    title: "Diferencias de recepción",
    subtitle: "Faltantes, sobrantes y notas obligatorias visibles antes de cierre.",
    status: "Diferencias por revisar",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Diferencias", title: "1 recepción", tone: "warn" as const, lines: ["faltan 4 piezas", "requiere motivo"] },
      { eyebrow: "Auditoría", title: "Nota obligatoria", tone: "warn" as const, lines: ["sin nota no cerrar", "actor visible"] },
      { eyebrow: "Inventario", title: "Movimiento condicionado", tone: "info" as const, lines: ["ajuste tras confirmación", "no automático"] }
    ],
    recommendedAction: {
      title: "Resolver diferencia antes de cerrar recepción.",
      motive: "las diferencias deben verse como bloqueo operativo, no como detalle enterrado.",
      actions: [
        { label: "Recibir proveedor", href: "/recepcion-proveedor", primary: true },
        { label: "Volver a recepción", href: "/receiving" },
        { label: "Ver orden", href: "/ordenes-compra" }
      ]
    },
    tableTitle: "Diferencias abiertas",
    tableSubtitle: "Faltantes y motivos que impiden cierre limpio.",
    columns: ["Recepción", "Producto", "Diferencia", "Acción"],
    rows: [
      { Recepción: "REC-103", Producto: "Refresco lata", Diferencia: "-4 piezas", Acción: "Capturar motivo" },
      { Recepción: "REC-103", Producto: "Jugo familiar", Diferencia: "0", Acción: "Confirmado" },
      { Recepción: "REC-102", Producto: "Agua mineral", Diferencia: "0", Acción: "Listo" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/incidencias-recepcion" },
      { kind: "technical" as const, label: "Corrección", value: "currentPath propio, no alias /receiving" },
      { kind: "technical" as const, label: "Scope", value: "diferencias y bloqueo operativo" }
    ]
  },
  "/senal-reabasto": {
    title: "Señal de reabasto",
    subtitle: "Señal puntual que explica por qué conviene pedir, sin confundirse con /replenishment.",
    status: "Señal activa",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Señal", title: "Bebidas prioridad", tone: "info" as const, lines: ["mínimos cercanos", "demanda reciente"] },
      { eyebrow: "Acción", title: "Crear sugerido", tone: "warn" as const, lines: ["validar proveedor", "pasar a orden"] },
      { eyebrow: "Confianza", title: "Media alta", tone: "info" as const, lines: ["stock + ventas", "requiere revisión"] }
    ],
    recommendedAction: {
      title: "Revisar señal y convertirla si aplica.",
      motive: "la señal debe explicar el motivo antes de convertirse en pedido.",
      actions: [
        { label: "Ver reabasto", href: "/replenishment", primary: true },
        { label: "Ver forecast", href: "/forecast-basico" },
        { label: "Crear orden", href: "/ordenes-compra" }
      ]
    },
    tableTitle: "Señales activas",
    tableSubtitle: "Motivos y prioridad del reabasto recomendado.",
    columns: ["Señal", "Motivo", "Prioridad", "Destino"],
    rows: [
      { Señal: "Bebidas", Motivo: "mínimo cercano", Prioridad: "Alta", Destino: "Reabasto" },
      { Señal: "Abarrotes", Motivo: "venta alta", Prioridad: "Media", Destino: "Forecast" },
      { Señal: "Lácteos", Motivo: "rotación estable", Prioridad: "Baja", Destino: "Monitorear" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/senal-reabasto" },
      { kind: "technical" as const, label: "Corrección", value: "currentPath propio, no alias /replenishment" },
      { kind: "technical" as const, label: "Scope", value: "señal explicativa" }
    ]
  },
  "/forecast-basico": {
    title: "Pronóstico básico",
    subtitle: "Lectura simple de demanda para apoyar compra sin crear órdenes automáticamente.",
    status: "Forecast disponible",
    lastUpdated: "Lectura actual",
    summaryCards: [
      { eyebrow: "Demanda", title: "Tendencia estable", tone: "info" as const, lines: ["bebidas suben", "abarrotes sostienen"] },
      { eyebrow: "Compra", title: "8 sugeridos", tone: "info" as const, lines: ["validar stock", "comparar proveedor"] },
      { eyebrow: "Riesgo", title: "Sin automatizar", tone: "warn" as const, lines: ["forecast no compra", "requiere decisión"] }
    ],
    recommendedAction: {
      title: "Usar forecast como apoyo, no como orden automática.",
      motive: "la predicción debe alimentar reabasto y órdenes, no reemplazar revisión humana.",
      actions: [
        { label: "Ver reabasto", href: "/replenishment", primary: true },
        { label: "Ver señal", href: "/senal-reabasto" },
        { label: "Crear orden", href: "/ordenes-compra" }
      ]
    },
    tableTitle: "Forecast operativo",
    tableSubtitle: "Tendencias de compra para decidir reabasto.",
    columns: ["Familia", "Tendencia", "Riesgo", "Acción"],
    rows: [
      { Familia: "Bebidas", Tendencia: "Sube", Riesgo: "Quiebre", Acción: "Revisar reabasto" },
      { Familia: "Abarrotes", Tendencia: "Estable", Riesgo: "Medio", Acción: "Monitorear" },
      { Familia: "Lácteos", Tendencia: "Baja", Riesgo: "Bajo", Acción: "No pedir aún" }
    ],
    evidence: [
      { kind: "technical" as const, label: "Ruta", value: "/forecast-basico" },
      { kind: "technical" as const, label: "Corrección", value: "currentPath propio, no alias /replenishment" },
      { kind: "technical" as const, label: "Scope", value: "forecast de apoyo" }
    ]
  }
};

export function getPurchasingScreenContract(currentPath: string) {
  return purchasingRouteContracts[currentPath as keyof typeof purchasingRouteContracts] ?? purchasingScreenContract;
}
