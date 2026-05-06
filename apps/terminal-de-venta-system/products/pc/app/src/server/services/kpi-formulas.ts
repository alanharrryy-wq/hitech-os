export function netSales(grossCents: number, returnsCents: number, cancellationsCents = 0, discountsCents = 0) {
  return grossCents - returnsCents - cancellationsCents - discountsCents;
}

export function rate(numerator: number, denominator: number) {
  return denominator === 0 ? null : numerator / denominator;
}

export function safeAverage(total: number, count: number) {
  return count === 0 ? null : total / count;
}

export function fillRate(completedReceipts: number, totalOrders: number) {
  return rate(completedReceipts, totalOrders);
}

export function formatKpiNumber(value: number | null, suffix = "") {
  if (value === null || Number.isNaN(value)) return "sin datos";
  return `${new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 }).format(value)}${suffix}`;
}

export function formatKpiMoney(cents: number | null) {
  if (cents === null || Number.isNaN(cents)) return "sin datos";
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}
