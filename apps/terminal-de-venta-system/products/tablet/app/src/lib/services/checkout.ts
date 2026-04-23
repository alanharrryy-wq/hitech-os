export function getCheckoutConsole() {
  return {
    offlineMode: true,
    kpis: {
      pendingTotal: 1268,
      cashMix: 58,
      cardMix: 34,
      cancelRate: 3.2
    },
    queue: {
      ready: 5
    },
    queueRows: [
      { ticket: "TK-90302", customer: "Mostrador", items: 3, total: 168, status: "listo", tone: "ok" as const },
      { ticket: "TK-90301", customer: "Ruta 04", items: 7, total: 412, status: "requiere confirmacion", tone: "warn" as const },
      { ticket: "TK-90300", customer: "Mostrador", items: 1, total: 38, status: "listo", tone: "ok" as const },
      { ticket: "TK-90299", customer: "Mostrador", items: 5, total: 279, status: "sincronizando", tone: "warn" as const },
      { ticket: "TK-90298", customer: "Mayoreo local", items: 12, total: 371, status: "bloqueado", tone: "danger" as const }
    ],
    paymentMix: [
      { method: "Efectivo", amount: 7350, share: 58, tone: "ok" as const, note: "Todavia manda el billete sudado." },
      { method: "Tarjeta", amount: 4310, share: 34, tone: "warn" as const, note: "Terminal estable, pero con picos de demora." },
      { method: "Mixto", amount: 1020, share: 8, tone: "ok" as const, note: "Util para tickets grandes sin pleito en caja." }
    ],
    blockers: [
      {
        title: "Barcode ilegible en linea 3",
        level: "vigilar",
        tone: "warn" as const,
        description: "El ticket TK-90301 trae un producto capturado a mano y pide confirmacion antes de cobrar.",
        action: "accion sugerida: revisar SKU BOT-1L antes del cierre"
      },
      {
        title: "Ticket con devolucion parcial previa",
        level: "critico",
        tone: "danger" as const,
        description: "El ticket TK-90298 tiene una devolucion parcial abierta y no debe cobrarse doble.",
        action: "accion sugerida: abrir historial y validar folio origen"
      },
      {
        title: "Cobro offline disponible",
        level: "ok",
        tone: "ok" as const,
        description: "La cola local sigue recibiendo tickets aunque la red central ande con sueno.",
        action: "accion sugerida: confirmar outbox al reconectar"
      }
    ],
    stockGuardrails: [
      {
        title: "SKU en quiebre dentro del ticket",
        level: "critico",
        tone: "danger" as const,
        description: "TK-90298 incluye REF-355ML en cantidad mayor a la existencia sincronizada del turno.",
        action: "accion sugerida: bloquear cobro asistido y ofrecer sustitucion"
      },
      {
        title: "Precio dudoso antes del cierre",
        level: "alerta",
        tone: "warn" as const,
        description: "CHO-CLAS trae diferencia entre anaquel y caja. Si se cobra asi, luego llega la devolucion con mariachis.",
        action: "accion sugerida: validar precio maestro o retener linea"
      },
      {
        title: "Reabasto corto disponible",
        level: "ok",
        tone: "ok" as const,
        description: "PAP-ADOBO tiene resurtido express a menos de 2 minutos y evita cancelar combo completo.",
        action: "accion sugerida: lanzar pedido rapido desde stock operativo"
      }
    ],
    substitutionHints: [
      { sku: "REF-355ML", alternative: "REF-600ML", note: "mantiene categoria y margen", tone: "warn" as const },
      { sku: "PAP-ADOBO", alternative: "PAP-SAL", note: "sustitucion rapida en anaquel vecino", tone: "ok" as const },
      { sku: "BOT-1L", alternative: "BOT-600ML x2", note: "misma salida con cobro controlado", tone: "ok" as const }
    ],
    shortcuts: [
      { kicker: "atajo", title: "Cobro en efectivo", description: "Cerrar ticket con importe exacto y confirmar en un toque." },
      { kicker: "atajo", title: "Cobro mixto", description: "Separar efectivo y tarjeta sin abrir un laberinto." },
      { kicker: "atajo", title: "Reimprimir folio", description: "Recuperar ticket reciente sin salir del flujo." },
      { kicker: "atajo", title: "Bloquear para revision", description: "Sacar del carril rapido un ticket con bronca visible." }
    ]
  };
}
