import { ShiftRepositoryPrisma } from "@/server/repositories/shift-repository.prisma";

const shiftRepository = new ShiftRepositoryPrisma();

function pesos(cents: number | null | undefined) {
  return (cents ?? 0) / 100;
}

function timeLabel(value: Date | string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(value));
}

function shiftTone(status: string, varianceCents: number | null | undefined) {
  if (status === "OPEN" && Math.abs(varianceCents ?? 0) > 0) return "warn" as const;
  return "ok" as const;
}

export async function getShiftConsole() {
  const [activeShift, recentShifts] = await Promise.all([
    shiftRepository.findOpenSessionByTerminal("terminal_tablet_01"),
    shiftRepository.listRecent(5)
  ]);

  const open = activeShift ?? recentShifts[0];

  return {
    activeShift: {
      cashier: open?.cashier ?? "sin operador",
      store: "Sucursal Obrera 04",
      openedAt: timeLabel(open?.openedAt),
      status: open?.status === "OPEN" ? "abierto" : "sin turno abierto",
      pendingIncidents: Math.abs(open?.varianceCents ?? 0) > 0 ? 1 : 0
    },
    kpis: {
      cashStart: pesos(open?.cashStartCents),
      salesTotal: pesos((open?.expectedCashCents ?? 0) - (open?.cashStartCents ?? 0)),
      expectedCash: pesos(open?.expectedCashCents),
      variance: pesos(open?.varianceCents)
    },
    snapshot: [
      { label: "Turno canónico", value: open?.id ?? "-", status: open?.status ?? "sin datos", tone: shiftTone(open?.status ?? "", open?.varianceCents) },
      { label: "Terminal", value: open?.terminalId ?? "terminal_tablet_01", status: "Prisma", tone: "ok" as const },
      { label: "Fondo inicial", value: `$${pesos(open?.cashStartCents).toFixed(2)}`, status: "persistido", tone: "ok" as const },
      { label: "Variación", value: `$${pesos(open?.varianceCents).toFixed(2)}`, status: "calculada", tone: shiftTone(open?.status ?? "", open?.varianceCents) }
    ],
    cashEvents: [],
    alerts: [
      {
        title: "CashSession abierta única",
        level: open?.status === "OPEN" ? "ok" : "pendiente",
        tone: open?.status === "OPEN" ? ("ok" as const) : ("warn" as const),
        description: "La vista lee el turno desde CashSession canónico por terminal.",
        action: "No abrir segundo turno para la misma terminal."
      }
    ],
    quickActions: [
      { kicker: "atajo", title: "Abrir turno", description: "Configura fondo inicial y operador." },
      { kicker: "atajo", title: "Registrar retiro", description: "Salida de efectivo con motivo y autorización." },
      { kicker: "atajo", title: "Corte parcial", description: "Conteo rápido sin cerrar caja completa." },
      { kicker: "atajo", title: "Cerrar turno", description: "Resumen final con diferencias y pendientes." }
    ],
    recentShifts: recentShifts.map((shift) => ({
      label: shift.id,
      cashier: shift.cashier,
      tickets: 0,
      netSales: pesos((shift.expectedCashCents ?? 0) - shift.cashStartCents),
      variance: pesos(shift.varianceCents),
      status: shift.status,
      tone: shiftTone(shift.status, shift.varianceCents)
    }))
  };
}
