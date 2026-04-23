export function mx(value: number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 2 }).format(value);
}

export function badgeTone(value: number) {
  if (value <= 0) return "verde";
  if (value < 100) return "ambar";
  return "rojo";
}
