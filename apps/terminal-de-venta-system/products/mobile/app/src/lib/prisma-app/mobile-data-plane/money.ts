export function clampInt(value: unknown, fallback = 0): number {
  const numberValue = typeof value === "number" ? value : typeof value === "string" ? Number.parseFloat(value) : Number.NaN;
  if (!Number.isFinite(numberValue)) return fallback;
  return Math.trunc(numberValue);
}

export function clampNonNegativeInt(value: unknown, fallback = 0): number {
  return Math.max(0, clampInt(value, fallback));
}

export function centsFromUnknown(value: unknown): number {
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value;
    return Math.round(value * 100);
  }
  if (typeof value === "string") {
    const cleaned = value.replace(/[$,\s]/g, "");
    const parsed = Number.parseFloat(cleaned);
    if (!Number.isFinite(parsed)) return 0;
    return Math.round(parsed * 100);
  }
  return 0;
}

export function moneyLabel(cents: number): string {
  const safe = Number.isFinite(cents) ? cents : 0;
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(safe / 100);
}

export function signedMoneyLabel(cents: number): string {
  if (cents === 0) return "$0";
  return `${cents > 0 ? "+" : "-"}${moneyLabel(Math.abs(cents))}`;
}

export function percentHeight(amountCents: number, maxCents: number): string {
  if (maxCents <= 0) return "6%";
  const pct = Math.max(6, Math.min(100, Math.round((amountCents / maxCents) * 100)));
  return `${pct}%`;
}

export function nowLabel(date = new Date()): string {
  return new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" }).format(date);
}

export function minutesAgoLabel(iso: string | null): string {
  if (!iso) return "sin sync";
  const time = Date.parse(iso);
  if (!Number.isFinite(time)) return "sync desconocido";
  const minutes = Math.max(0, Math.round((Date.now() - time) / 60000));
  if (minutes < 1) return "ahora";
  if (minutes === 1) return "hace 1 min";
  if (minutes < 60) return `hace ${minutes} min`;
  const hours = Math.round(minutes / 60);
  return hours === 1 ? "hace 1 h" : `hace ${hours} h`;
}
