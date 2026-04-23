export function getSyncConsole() {
  return {
    health: {
      title: "cola viva con advertencias",
      description: "La tablet siguió operando sin red, pero hay dos carriles que ya piden cariño antes del cierre.",
      lastSuccess: "hace 03 min"
    },
    kpis: {
      pending: 27,
      failed: 4,
      avgLatencyMs: 1280,
      offlineShare: 34
    },
    channels: [
      {
        name: "ventas",
        description: "tickets y cierres listos para salir al panel administrativo",
        pending: 14,
        retries: 3,
        maxAge: "12 min",
        load: 76,
        status: "presión alta",
        tone: "warn" as const
      },
      {
        name: "devoluciones",
        description: "folios con impacto en caja e inventario operativo",
        pending: 4,
        retries: 1,
        maxAge: "07 min",
        load: 38,
        status: "estable",
        tone: "ok" as const
      },
      {
        name: "turno",
        description: "aperturas, cierres y arqueos con trazabilidad",
        pending: 3,
        retries: 0,
        maxAge: "04 min",
        load: 24,
        status: "limpio",
        tone: "ok" as const
      },
      {
        name: "sincronización",
        description: "heartbeat, confirmaciones y eventos de conflicto",
        pending: 6,
        retries: 5,
        maxAge: "18 min",
        load: 91,
        status: "cuello de botella",
        tone: "danger" as const
      }
    ],
    alerts: [
      {
        title: "Conflicto de stock en SKU B-104",
        level: "crítico",
        tone: "danger" as const,
        description: "La tablet reporta una devolución recuperable, pero el panel central ya marcó merma para el mismo movimiento.",
        action: "Retener confirmación final y pedir resolución supervisada antes del siguiente reintento."
      },
      {
        title: "Outbox con edad alta",
        level: "alerta",
        tone: "warn" as const,
        description: "Hay eventos de venta con más de 10 minutos en cola y el turno ya va en tramo de alta demanda.",
        action: "Forzar lote corto de reintento en cuanto la red vuelva a respirar."
      },
      {
        title: "Latencia de confirmación estable",
        level: "controlado",
        tone: "ok" as const,
        description: "La mayoría de eventos recientes sí está regresando con confirmación en menos de 2 segundos.",
        action: "Mantener monitoreo sin bloquear operación."
      }
    ],
    pendingEvents: [
      { topic: "sale.created", aggregate: "TK-240418-181", age: "12 min", attempts: 3, status: "pendiente", tone: "warn" as const },
      { topic: "ticket.closed", aggregate: "TK-240418-181", age: "11 min", attempts: 3, status: "pendiente", tone: "warn" as const },
      { topic: "return.created", aggregate: "DV-240418-031", age: "07 min", attempts: 1, status: "pendiente", tone: "ok" as const },
      { topic: "sync.failed", aggregate: "HB-240418-022", age: "06 min", attempts: 5, status: "fallido", tone: "danger" as const },
      { topic: "shift.closed", aggregate: "TRN-240418-MAT", age: "04 min", attempts: 1, status: "pendiente", tone: "ok" as const }
    ],
    latency: [
      { stage: "persistencia local", avgMs: 44, p95Ms: 82, signal: "sano", tone: "ok" as const },
      { stage: "encolado outbox", avgMs: 118, p95Ms: 220, signal: "estable", tone: "ok" as const },
      { stage: "envío al panel", avgMs: 1280, p95Ms: 2840, signal: "vigilar", tone: "warn" as const },
      { stage: "confirmación final", avgMs: 1640, p95Ms: 3320, signal: "tenso", tone: "warn" as const }
    ],
    offlineRules: [
      { label: "Venta local permitida", value: "sí, con folio temporal", status: "activo", tone: "ok" as const },
      { label: "Límite de cola sin bloquear", value: "40 eventos", status: "27/40", tone: "ok" as const },
      { label: "Reintento automático", value: "cada 90 segundos", status: "activo", tone: "ok" as const },
      { label: "Conflictos sin resolver", value: "1 incidente", status: "revisar", tone: "warn" as const },
      { label: "Bloqueo de cierre por falla crítica", value: "habilitado", status: "activo", tone: "danger" as const }
    ]
  };
}
