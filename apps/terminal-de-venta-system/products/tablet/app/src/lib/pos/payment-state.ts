export type PaymentMethod = "cash" | "card" | "transfer";
export type PaymentMethodOrMixed = PaymentMethod | "mixed";

export type PaymentTenderInput = {
  id: PaymentMethod;
  method: PaymentMethod;
  amountCents: number;
  reference: string;
};

export type PaymentMethodDefinition = {
  id: PaymentMethod;
  label: string;
  requiresCashReceived: boolean;
  visibleConfirmation: string;
};

export const PAYMENT_METHODS: readonly PaymentMethodDefinition[] = [
  { id: "transfer", label: "Transferencia interbancaria", requiresCashReceived: false, visibleConfirmation: "Referencia opcional: puedes generar ticket sólo con importe confirmado." },
  { id: "card", label: "Tarjeta bancaria", requiresCashReceived: false, visibleConfirmation: "Autorización opcional: captura importe y confirma la terminal." },
  { id: "cash", label: "Efectivo", requiresCashReceived: true, visibleConfirmation: "Indica con qué billete o monedas paga el cliente para calcular cambio." }
] as const;

export function normalizePaymentMethod(value: unknown): PaymentMethod {
  return value === "card" || value === "transfer" || value === "cash" ? value : "cash";
}

export function paymentMethodDefinition(method: PaymentMethod): PaymentMethodDefinition {
  return PAYMENT_METHODS.find((item) => item.id === method) ?? PAYMENT_METHODS[2];
}

export function paymentMethodLabel(method: PaymentMethod | string | null | undefined) {
  if (method === "mixed") return "Pago mixto";
  return paymentMethodDefinition(normalizePaymentMethod(method)).label;
}

export function createDefaultPaymentTenders(): PaymentTenderInput[] {
  return [
    { id: "cash", method: "cash", amountCents: 0, reference: "" },
    { id: "card", method: "card", amountCents: 0, reference: "" },
    { id: "transfer", method: "transfer", amountCents: 0, reference: "" }
  ];
}

export function normalizePaymentTenders(value: PaymentTenderInput[] | null | undefined): PaymentTenderInput[] {
  const byMethod = new Map<PaymentMethod, PaymentTenderInput>();
  for (const tender of createDefaultPaymentTenders()) byMethod.set(tender.method, tender);
  for (const tender of value ?? []) {
    const method = normalizePaymentMethod(tender.method);
    byMethod.set(method, {
      id: method,
      method,
      amountCents: Math.max(0, Math.round(Number(tender.amountCents ?? 0))),
      reference: typeof tender.reference === "string" ? tender.reference : ""
    });
  }
  return createDefaultPaymentTenders().map((base) => byMethod.get(base.method) ?? base);
}
