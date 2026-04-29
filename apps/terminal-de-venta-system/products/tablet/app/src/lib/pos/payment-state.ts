export type PaymentMethod = "cash" | "card" | "transfer";

export const PAYMENT_METHODS: Array<{ value: PaymentMethod; label: string; helper: string }> = [
  { value: "cash", label: "Efectivo", helper: "Calcula cambio antes de cerrar." },
  { value: "card", label: "Tarjeta", helper: "Marca la venta como pagada con tarjeta." },
  { value: "transfer", label: "Transferencia", helper: "Útil cuando el cliente paga por SPEI o QR." }
];

export function paymentMethodLabel(value: string) {
  return PAYMENT_METHODS.find((method) => method.value === value)?.label ?? "Pago";
}
