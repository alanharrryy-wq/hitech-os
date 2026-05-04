import type { CanonicalCashState, CanonicalSalesToday, MobileDataPlaneConfig } from "./types";

export function deriveCashState(sales: CanonicalSalesToday, config: MobileDataPlaneConfig): CanonicalCashState {
  let cashInCents = 0;
  let cardCents = 0;
  let transferCents = 0;
  for (const sale of sales.sales) {
    const method = sale.paymentMethod.toLowerCase();
    if (method.includes("tarjeta") || method.includes("card")) cardCents += sale.totalCents;
    else if (method.includes("transfer") || method.includes("spei")) transferCents += sale.totalCents;
    else cashInCents += sale.totalCents;
  }
  const expectedCents = cashInCents;
  return {
    expectedCents,
    countedCents: null,
    differenceCents: 0,
    openedAt: sales.sales[0]?.createdAt ?? null,
    lastCutAt: null,
    cashInCents,
    cashOutCents: 0,
    cardCents,
    transferCents
  };
}

export function cashStatus(cash: CanonicalCashState, config: MobileDataPlaneConfig): string {
  const abs = Math.abs(cash.differenceCents);
  if (cash.countedCents === null) return "Caja operando sin conteo capturado";
  if (abs >= config.cashDifferenceCriticalCents) return "Diferencia crítica de caja";
  if (abs >= config.cashDifferenceWarningCents) return "Caja con diferencia por revisar";
  return "Caja cuadrada";
}
