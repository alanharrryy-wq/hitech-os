export function getReturnsConsole() {
  return {
    kpis: {
      returnCount: 14,
      cancelCount: 5,
      amountToday: 2860,
      avgRefund: 204,
      restockableRate: 71
    },
    topReason: {
      reason: "captura duplicada",
      count: 5
    },
    recentReturns: [
      { folio: "DV-240418-031", reason: "captura duplicada", amount: 158, cashier: "Mariela Soto", status: "cerrada", tone: "ok" as const },
      { folio: "DV-240418-028", reason: "producto dañado", amount: 420, cashier: "Luis Tovar", status: "revisión", tone: "warn" as const },
      { folio: "DV-240418-024", reason: "precio incorrecto", amount: 89, cashier: "Mariela Soto", status: "cerrada", tone: "ok" as const },
      { folio: "DV-240418-019", reason: "ticket sin firma", amount: 310, cashier: "Diana Reyna", status: "bloqueada", tone: "danger" as const }
    ],
    reasonMix: [
      { reason: "captura duplicada", count: 5, amount: 603, signal: "operación", tone: "warn" as const },
      { reason: "producto dañado", count: 3, amount: 1070, signal: "merma", tone: "danger" as const },
      { reason: "precio incorrecto", count: 4, amount: 487, signal: "catálogo", tone: "warn" as const },
      { reason: "cliente se arrepiente", count: 2, amount: 700, signal: "normal", tone: "ok" as const }
    ],
    guardrails: [
      {
        title: "Folio origen obligatorio",
        level: "obligatorio",
        tone: "ok" as const,
        description: "Toda devolución debe venir amarrada al ticket original o a una referencia de incidente.",
        action: "No permitir guardar hasta capturar folio o excepción supervisada."
      },
      {
        title: "Monto alto sin autorización",
        level: "alerta",
        tone: "warn" as const,
        description: "Devoluciones arriba de $500 MXN deben requerir supervisor o motivo reforzado.",
        action: "Solicitar firma o PIN antes del cierre del movimiento."
      },
      {
        title: "Producto sin retorno a inventario",
        level: "crítico",
        tone: "danger" as const,
        description: "Hay devoluciones marcadas como recuperables sin ajuste de stock confirmado.",
        action: "Bloquear cierre si no se registró restock o merma correspondiente."
      }
    ],
    quickActions: [
      { kicker: "atajo", title: "Nueva devolución", description: "Captura motivo, folio y monto con menos fricción." },
      { kicker: "atajo", title: "Cancelar ticket", description: "Reversa controlada con responsable visible." },
      { kicker: "atajo", title: "Enviar a merma", description: "Marca producto dañado para inventario operativo." },
      { kicker: "atajo", title: "Escalar excepción", description: "Manda bronca al supervisor con contexto del caso." }
    ],
    traceability: [
      { label: "Folio origen", value: "100% requerido", status: "cubierto", tone: "ok" as const },
      { label: "Responsable visible", value: "operador + supervisor", status: "cubierto", tone: "ok" as const },
      { label: "Motivo estandarizado", value: "4 categorías activas", status: "estable", tone: "ok" as const },
      { label: "Impacto en inventario", value: "3 casos pendientes", status: "revisar", tone: "warn" as const },
      { label: "Excepciones sin firma", value: "1 caso bloqueado", status: "crítico", tone: "danger" as const }
    ]
  };
}
