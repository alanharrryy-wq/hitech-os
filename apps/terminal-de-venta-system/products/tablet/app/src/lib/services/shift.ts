export function getShiftConsole() {
  return {
    activeShift: {
      cashier: "Mariela Soto",
      store: "Sucursal Obrera 04",
      openedAt: "06:55",
      status: "abierto y estable",
      pendingIncidents: 2
    },
    kpis: {
      cashStart: 2500,
      salesTotal: 18340,
      expectedCash: 9630,
      variance: -120
    },
    snapshot: [
      { label: "Tickets cerrados", value: "146", status: "al día", tone: "ok" as const },
      { label: "Tiempo promedio de venta", value: "01:48", status: "estable", tone: "ok" as const },
      { label: "Retiros de efectivo", value: "2", status: "revisar último retiro", tone: "warn" as const },
      { label: "Eventos offline", value: "3", status: "pendientes de sync", tone: "warn" as const },
      { label: "Conteo parcial", value: "$9,510", status: "desfase detectado", tone: "danger" as const }
    ],
    cashEvents: [
      { time: "07:00", label: "Apertura con fondo", amount: 2500, status: "confirmado", tone: "ok" as const },
      { time: "10:35", label: "Retiro por seguridad", amount: -3000, status: "validado", tone: "ok" as const },
      { time: "13:10", label: "Ingreso por cambio", amount: 400, status: "capturado", tone: "ok" as const },
      { time: "16:22", label: "Arqueo parcial", amount: 9510, status: "requiere ajuste", tone: "warn" as const }
    ],
    alerts: [
      {
        title: "Variación contra conteo parcial",
        level: "alerta",
        tone: "warn" as const,
        description: "Hay una diferencia de $120 MXN entre el efectivo esperado y el conteo parcial del turno.",
        action: "Pedir reconteo antes del cierre y registrar comentario del operador."
      },
      {
        title: "Tickets offline por enviar",
        level: "pendiente",
        tone: "warn" as const,
        description: "Tres tickets siguen en cola local y pueden contaminar el cierre si no se sincronizan.",
        action: "Forzar reintento de sync antes de imprimir corte final."
      },
      {
        title: "Retiro sin firma de supervisor",
        level: "crítico",
        tone: "danger" as const,
        description: "El retiro de las 10:35 no tiene evidencia de autorización adjunta.",
        action: "Bloquear cierre hasta capturar supervisor o justificar incidente."
      }
    ],
    quickActions: [
      { kicker: "atajo", title: "Abrir turno", description: "Configura fondo inicial y operador en menos toques." },
      { kicker: "atajo", title: "Registrar retiro", description: "Salida de efectivo con motivo y autorización." },
      { kicker: "atajo", title: "Corte parcial", description: "Conteo rápido sin cerrar caja completa." },
      { kicker: "atajo", title: "Cerrar turno", description: "Resumen final con diferencias y pendientes." }
    ],
    recentShifts: [
      { label: "Matutino", cashier: "Mariela Soto", tickets: 146, netSales: 18340, variance: -120, status: "en curso", tone: "warn" as const },
      { label: "Nocturno", cashier: "Luis Tovar", tickets: 158, netSales: 20120, variance: 0, status: "cerrado limpio", tone: "ok" as const },
      { label: "Especial promo", cashier: "Diana Reyna", tickets: 97, netSales: 12310, variance: 80, status: "ajustado", tone: "warn" as const }
    ]
  };
}
