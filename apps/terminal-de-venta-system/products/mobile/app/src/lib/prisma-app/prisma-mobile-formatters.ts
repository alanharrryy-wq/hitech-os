const mxnFormatter = new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 });
const numberFormatter = new Intl.NumberFormat("es-MX");

export function formatMxnFromCents(cents: number): string {
  return mxnFormatter.format(cents / 100);
}

export function formatSignedMxnFromCents(cents: number): string {
  if (cents === 0) return "$0";
  const sign = cents > 0 ? "+" : "-";
  return `${sign}${formatMxnFromCents(Math.abs(cents))}`;
}

export function formatInteger(value: number): string {
  return numberFormatter.format(value);
}

export function safePercentHeight(value: string): string {
  return /^\d{1,3}%$/.test(value) ? value : "0%";
}

export function formatRelativeFetchLabel(isoDate: string): string {
  const timestamp = Date.parse(isoDate);
  if (Number.isNaN(timestamp)) return "actualización reciente";
  const diffSeconds = Math.floor(Math.max(0, Date.now() - timestamp) / 1000);
  if (diffSeconds < 20) return "hace unos segundos";
  if (diffSeconds < 60) return `hace ${diffSeconds} segundos`;
  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) return `hace ${diffMinutes} min`;
  return `hace ${Math.floor(diffMinutes / 60)} h`;
}
