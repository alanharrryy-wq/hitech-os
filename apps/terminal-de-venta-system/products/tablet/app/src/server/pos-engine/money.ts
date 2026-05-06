import { PosEngineError } from "./errors";

export function toCents(value: number) {
  if (!Number.isFinite(value)) {
    throw new PosEngineError("ENGINE_INVARIANT_FAILED", "Monto inválido para convertir a centavos.", { value });
  }
  return Math.round(value * 100);
}

export function addCents(values: number[]) {
  return values.reduce((sum, value) => sum + value, 0);
}

export function multiplyCents(unitCents: number, qty: number) {
  if (!Number.isInteger(unitCents) || unitCents < 0) {
    throw new PosEngineError("ENGINE_INVARIANT_FAILED", "Precio inválido en centavos.", { unitCents });
  }
  if (!Number.isInteger(qty) || qty <= 0) {
    throw new PosEngineError("INVALID_QUANTITY", "Cantidad inválida para multiplicar precio.", { qty });
  }
  return unitCents * qty;
}

export function formatMxCurrency(cents: number) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN"
  }).format(cents / 100);
}
