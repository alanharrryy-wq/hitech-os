import { ReturnRepositoryPrisma } from "@/server/repositories/return-repository.prisma";

const returnRepository = new ReturnRepositoryPrisma();

function pesos(cents: number) {
  return cents / 100;
}

function returnTone(status: string) {
  return status === "closed" ? ("ok" as const) : ("warn" as const);
}

export async function getReturnsConsole() {
  const returns = await returnRepository.listRecent(25);
  const amountToday = returns.reduce((acc, row) => acc + row.amountCents, 0);
  const reasonCounts = new Map<string, { count: number; amount: number }>();
  for (const row of returns) {
    const current = reasonCounts.get(row.reason) ?? { count: 0, amount: 0 };
    current.count += 1;
    current.amount += row.amountCents;
    reasonCounts.set(row.reason, current);
  }
  const reasonMix = Array.from(reasonCounts.entries()).map(([reason, value]) => ({
    reason,
    count: value.count,
    amount: pesos(value.amount),
    signal: value.amount > 50000 ? "vigilar" : "normal",
    tone: value.amount > 50000 ? ("warn" as const) : ("ok" as const)
  }));
  const topReason = reasonMix[0] ?? { reason: "-", count: 0 };

  return {
    kpis: {
      returnCount: returns.length,
      cancelCount: 0,
      amountToday: pesos(amountToday),
      avgRefund: returns.length ? pesos(amountToday) / returns.length : 0,
      restockableRate: 100
    },
    topReason,
    recentReturns: returns.slice(0, 6).map((row) => ({
      folio: row.id,
      reason: row.reason,
      amount: pesos(row.amountCents),
      cashier: row.cashier,
      status: row.status,
      tone: returnTone(row.status)
    })),
    reasonMix,
    guardrails: [
      {
        title: "Folio origen obligatorio",
        level: "obligatorio",
        tone: "ok" as const,
        description: "Toda devolución queda ligada a saleFolio en SaleReturn.",
        action: "Validar folio antes de cerrar la devolución."
      },
      {
        title: "Devoluciones Prisma",
        level: "ok",
        tone: "ok" as const,
        description: "La consola lee devoluciones desde el modelo canónico.",
        action: "No usar arreglos demo para decisiones de caja."
      }
    ],
    quickActions: [
      { kicker: "atajo", title: "Nueva devolución", description: "Captura motivo, folio y monto." },
      { kicker: "atajo", title: "Cancelar ticket", description: "Reversa controlada con responsable visible." },
      { kicker: "atajo", title: "Enviar a merma", description: "Marca producto dañado para inventario operativo." },
      { kicker: "atajo", title: "Escalar excepción", description: "Manda el caso al supervisor con contexto." }
    ],
    traceability: [
      { label: "Folio origen", value: "SaleReturn.saleFolio", status: "persistido", tone: "ok" as const },
      { label: "Responsable visible", value: "cashier", status: "persistido", tone: "ok" as const },
      { label: "Motivo", value: `${reasonMix.length} motivos`, status: "persistido", tone: "ok" as const }
    ]
  };
}
