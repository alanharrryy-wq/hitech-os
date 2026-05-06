export type PaymentMethod = "cash" | "card" | "transfer";

export type PaymentMethodDefinition = {
  id: PaymentMethod;
  label: string;
  requiresCashReceived: boolean;
  visibleConfirmation: string;
};

export const PAYMENT_METHODS: readonly PaymentMethodDefinition[] = [
  { id: "transfer", label: "Transferencia interbancaria", requiresCashReceived: false, visibleConfirmation: "Confirma comprobante o referencia antes de generar ticket." },
  { id: "card", label: "Tarjeta bancaria", requiresCashReceived: false, visibleConfirmation: "Confirma aprobación en terminal bancaria antes de generar ticket." },
  { id: "cash", label: "Efectivo", requiresCashReceived: true, visibleConfirmation: "Indica con qué billete o monedas paga el cliente para calcular cambio." }
] as const;

export function normalizePaymentMethod(value: unknown): PaymentMethod {
  return value === "card" || value === "transfer" || value === "cash" ? value : "cash";
}

export function paymentMethodDefinition(method: PaymentMethod): PaymentMethodDefinition {
  return PAYMENT_METHODS.find((item) => item.id === method) ?? PAYMENT_METHODS[2];
}

export function paymentMethodLabel(method: PaymentMethod | string | null | undefined) {
  return paymentMethodDefinition(normalizePaymentMethod(method)).label;
}
