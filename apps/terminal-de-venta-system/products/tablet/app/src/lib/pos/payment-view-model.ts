
import type { CartLine } from "./cart-state";
import { cartTotalCents, cartTotalQty } from "./cart-state";
import { validateCartForCheckout } from "./cart-engine";
import type { PaymentMethod, PaymentMethodOrMixed, PaymentTenderInput } from "./payment-state";
import { normalizePaymentTenders, paymentMethodLabel } from "./payment-state";

export function buildPaymentReviewViewModel(input: { lines: CartLine[]; paymentTenders?: PaymentTenderInput[]; paymentMethod?: PaymentMethod; cashReceivedCents?: number }) {
  const ready = validateCartForCheckout(input.lines);
  const totalCents = cartTotalCents(input.lines);
  const paymentTenders = normalizePaymentTenders(
    input.paymentTenders ?? (input.paymentMethod ? [{ id: input.paymentMethod, method: input.paymentMethod, amountCents: input.cashReceivedCents ?? totalCents, reference: "" }] : undefined)
  );
  const activeTenders = paymentTenders.filter((tender) => tender.amountCents > 0);
  const paidCents = activeTenders.reduce((sum, tender) => sum + tender.amountCents, 0);
  const cashPaidCents = activeTenders.filter((tender) => tender.method === "cash").reduce((sum, tender) => sum + tender.amountCents, 0);
  const nonCashPaidCents = paidCents - cashPaidCents;
  const remainingCents = Math.max(0, totalCents - paidCents);
  const nonCashOverpayCents = Math.max(0, nonCashPaidCents - totalCents);
  const changeCents = nonCashOverpayCents > 0 ? 0 : Math.max(0, paidCents - totalCents);
  const paymentMethod: PaymentMethodOrMixed = activeTenders.length === 1 ? activeTenders[0].method : activeTenders.length > 1 ? "mixed" : "cash";
  const paymentLabel = paymentMethodLabel(paymentMethod);
  const tenderLabel = !ready.ready
    ? "Ticket pendiente"
    : !activeTenders.length
      ? "Falta capturar pago"
      : nonCashOverpayCents > 0
        ? "Corrige tarjeta o transferencia"
        : paidCents < totalCents
          ? "Pago incompleto"
          : changeCents > 0
            ? "Cambio calculado"
            : "Pago listo para ticket";
  const tenderDetail = !ready.ready
    ? ready.reason
    : !activeTenders.length
      ? "Captura efectivo, tarjeta o transferencia para cerrar el ticket."
      : nonCashOverpayCents > 0
        ? "Tarjeta o transferencia no deben exceder el total pendiente; el cambio solo sale de efectivo."
        : paidCents < totalCents
          ? "El pago todavía no cubre el total. Agrega otro método de pago, ajusta el importe o completa el saldo pendiente."
          : changeCents > 0
            ? "Entrega el cambio calculado desde efectivo y toca OK para generar ticket."
            : "Confirma comprobante o efectivo exacto y toca OK para generar ticket.";

  return {
    totalCents,
    totalQty: cartTotalQty(input.lines),
    totalLines: input.lines.length,
    paymentLabel,
    paymentMethod,
    paymentTenders,
    tenders: activeTenders,
    paidCents,
    cashPaidCents,
    nonCashPaidCents,
    remainingCents,
    nonCashOverpayCents,
    cashReceivedCents: cashPaidCents > 0 ? cashPaidCents : null,
    canConfirm: ready.ready && activeTenders.length > 0 && paidCents >= totalCents && nonCashOverpayCents === 0,
    blockReason: !ready.ready || !activeTenders.length || paidCents < totalCents || nonCashOverpayCents > 0 ? tenderDetail : null,
    cashMissingCents: remainingCents,
    changeCents,
    tenderLabel,
    tenderDetail
  };
}
