export function getHardeningConsole() {
  return {
    releaseTitle: "Hardening activo: lista corta de cosas que aún pueden torcer la jornada",
    releaseDescription: "La tablet ya aguanta venta, turno, devoluciones, stock y sync, pero t06 mete candados para que los errores no se escondan ni se vuelvan bola de nieve.",
    releaseAction: "prioridad: resolver bloqueo de cierre por outbox crítico y variación sin firma antes del siguiente corte",
    releaseTone: "warn" as const,
    blockers: [
      {
        title: "Cierre con eventos críticos en cola",
        description: "Hay un heartbeat fallido y un ticket con confirmación pendiente arriba del umbral sano.",
        level: "bloquea release",
        tone: "danger" as const,
        action: "bajar cola crítica debajo de 2 incidentes antes de declarar turno limpio"
      },
      {
        title: "Variación de caja sin autorización completa",
        description: "El retiro del turno matutino todavía no trae evidencia cerrada del supervisor.",
        level: "revisar",
        tone: "warn" as const,
        action: "adjuntar firma o comentario de excepción antes de consolidar corte"
      }
    ],
    smokeChecks: [
      { label: "ventas renderizan con top SKU", result: "ok", evidence: "lista con 5 productos y señales de stock", status: "estable", tone: "ok" as const },
      { label: "checkout muestra bloqueos", result: "ok", evidence: "3 candados visibles y sustituciones activas", status: "estable", tone: "ok" as const },
      { label: "devoluciones exigen folio", result: "ok", evidence: "guardrail obligatorio presente", status: "estable", tone: "ok" as const },
      { label: "sync conserva conflictos visibles", result: "ok", evidence: "1 incidente crítico y tabla de latencia", status: "vigilar", tone: "warn" as const },
      { label: "stock avisa quiebres", result: "ok", evidence: "watchlist con 2 riesgos calientes", status: "vigilar", tone: "warn" as const },
      { label: "runtime fallback", result: "nuevo", evidence: "error.tsx y not-found activos en t06", status: "listo", tone: "ok" as const }
    ],
    recovery: [
      {
        title: "Fallback de runtime",
        description: "Si una vista truena, la app ya no deja pantalla muerta. Enseña contexto, pasos y botón de reintento.",
        level: "nuevo",
        tone: "ok" as const,
        action: "usar reintento local antes de reabrir la sesión completa"
      },
      {
        title: "Ruta perdida controlada",
        description: "Si alguien cae en una URL rota, la app lo regresa con calma en lugar de aventarlo al vacío.",
        level: "nuevo",
        tone: "ok" as const,
        action: "volver al tablero y navegar por shell normal"
      },
      {
        title: "Incidencias visibles",
        description: "Los bloqueos y checks ya están en Inicio, así que el supervisor no necesita adivinar salud operativa.",
        level: "operativo",
        tone: "warn" as const,
        action: "usar tablero como semáforo antes de cierre y despliegue"
      }
    ]
  };
}
