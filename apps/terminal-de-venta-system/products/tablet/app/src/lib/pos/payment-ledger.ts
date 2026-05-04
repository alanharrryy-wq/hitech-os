export type PaymentLedgerEntryType =
  | "sale_total"
  | "cash_received"
  | "cash_change"
  | "card_capture"
  | "transfer_reference"
  | "mixed_payment_note"
  | "rounding_adjustment"
  | "operator_notice";

export type PaymentLedgerEntry = {
  type: PaymentLedgerEntryType;
  label: string;
  amountCents: number;
  visibleAmount: string;
  severity: "info" | "success" | "warning" | "danger";
  sortOrder: number;
  operatorCopy: string;
};

export type PaymentLedgerInput = {
  totalCents: number;
  paymentMethod: "cash" | "card" | "transfer" | "mixed";
  cashReceivedCents?: number;
  transferReference?: string;
  cardAuthorization?: string;
  locale?: string;
  currency?: string;
};

export type PaymentLedgerSummary = {
  totalCents: number;
  receivedCents: number;
  changeCents: number;
  balanceCents: number;
  canClose: boolean;
  blockingReason: string | null;
  entries: PaymentLedgerEntry[];
};

export function formatLedgerMoney(cents: number, locale = "es-MX", currency = "MXN") {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(cents / 100);
}

export function buildPaymentLedger(input: PaymentLedgerInput): PaymentLedgerSummary {
  const locale = input.locale ?? "es-MX";
  const currency = input.currency ?? "MXN";
  const totalCents = Math.max(0, Math.round(input.totalCents));
  const entries: PaymentLedgerEntry[] = [];
  const push = (entry: Omit<PaymentLedgerEntry, "visibleAmount">) => {
    entries.push({ ...entry, visibleAmount: formatLedgerMoney(entry.amountCents, locale, currency) });
  };

  push({
    type: "sale_total",
    label: "Total de la venta",
    amountCents: totalCents,
    severity: "info",
    sortOrder: 10,
    operatorCopy: "Este es el total que debe quedar cubierto antes de cerrar el ticket.",
  });

  if (input.paymentMethod === "cash") {
    const receivedCents = Math.max(0, Math.round(input.cashReceivedCents ?? 0));
    const changeCents = Math.max(0, receivedCents - totalCents);
    const balanceCents = Math.max(0, totalCents - receivedCents);
    push({
      type: "cash_received",
      label: "Efectivo recibido",
      amountCents: receivedCents,
      severity: receivedCents >= totalCents ? "success" : "warning",
      sortOrder: 20,
      operatorCopy: receivedCents >= totalCents ? "El efectivo cubre la venta." : "Falta efectivo para cerrar la venta.",
    });
    if (changeCents > 0) {
      push({
        type: "cash_change",
        label: "Cambio a entregar",
        amountCents: changeCents,
        severity: "success",
        sortOrder: 30,
        operatorCopy: "Entrega este cambio antes de cerrar físicamente el ticket.",
      });
    }
    return { totalCents, receivedCents, changeCents, balanceCents, canClose: balanceCents === 0, blockingReason: balanceCents ? `Faltan ${formatLedgerMoney(balanceCents, locale, currency)} para cerrar.` : null, entries: entries.sort((a, b) => a.sortOrder - b.sortOrder) };
  }

  if (input.paymentMethod === "card") {
    push({
      type: "card_capture",
      label: "Pago con tarjeta",
      amountCents: totalCents,
      severity: input.cardAuthorization ? "success" : "warning",
      sortOrder: 20,
      operatorCopy: input.cardAuthorization ? `Autorización: ${input.cardAuthorization}` : "Confirma la terminal bancaria antes de cerrar.",
    });
    return { totalCents, receivedCents: totalCents, changeCents: 0, balanceCents: 0, canClose: true, blockingReason: null, entries: entries.sort((a, b) => a.sortOrder - b.sortOrder) };
  }

  if (input.paymentMethod === "transfer") {
    push({
      type: "transfer_reference",
      label: "Transferencia",
      amountCents: totalCents,
      severity: input.transferReference ? "success" : "warning",
      sortOrder: 20,
      operatorCopy: input.transferReference ? `Referencia: ${input.transferReference}` : "Registra la referencia si el negocio la exige.",
    });
    return { totalCents, receivedCents: totalCents, changeCents: 0, balanceCents: 0, canClose: true, blockingReason: null, entries: entries.sort((a, b) => a.sortOrder - b.sortOrder) };
  }

  push({
    type: "mixed_payment_note",
    label: "Pago mixto",
    amountCents: totalCents,
    severity: "info",
    sortOrder: 20,
    operatorCopy: "Pago mixto queda preparado para fase posterior; por ahora se usa como señal visible, no como split contable.",
  });
  return { totalCents, receivedCents: totalCents, changeCents: 0, balanceCents: 0, canClose: true, blockingReason: null, entries: entries.sort((a, b) => a.sortOrder - b.sortOrder) };
}
