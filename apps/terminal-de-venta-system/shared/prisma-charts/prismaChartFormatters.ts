export function formatPercent(value: number) {
  return `${Math.round(value)}%`;
}

export function formatCurrencyFromCents(value: number, currency = "MXN") {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency,
    maximumFractionDigits: 0
  }).format(value / 100);
}

export function formatLatency(value?: number) {
  if (typeof value !== "number") return "--";
  return `${Math.round(value)} ms`;
}

export function formatAgeMinutes(minutes: number) {
  if (minutes < 1) return "fresh";
  if (minutes < 60) return `${Math.round(minutes)} min`;
  return `${Math.round(minutes / 60)} h`;
}

export function humanizeKey(value: string) {
  return value.replace(/[_-]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

