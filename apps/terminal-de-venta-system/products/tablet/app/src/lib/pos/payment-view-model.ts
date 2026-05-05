
import type { CartLine } from "./cart-state";
import { cartTotalCents, cartTotalQty } from "./cart-state";
import { validateCartForCheckout } from "./cart-engine";
import type { PaymentMethod } from "./payment-state";
import { paymentMethodDefinition } from "./payment-state";
import { reviewCashTender } from "./payment-tender";

export function buildPaymentReviewViewModel(input: { lines: CartLine[]; paymentMethod: PaymentMethod; cashReceivedCents: number }) {
  const ready = validateCartForCheckout(input.lines);
  const totalCents = cartTotalCents(input.lines);
  const tender = reviewCashTender(input.paymentMethod, totalCents, input.cashReceivedCents);
  const payment = paymentMethodDefinition(input.paymentMethod);

  return {
    totalCents,
    totalQty: cartTotalQty(input.lines),
    totalLines: input.lines.length,
    paymentLabel: payment.label,
    canConfirm: ready.ready && tender.canContinue,
    blockReason: !ready.ready ? ready.reason : !tender.canContinue ? tender.visibleDetail : null,
    cashMissingCents: tender.missingCents,
    changeCents: tender.changeCents,
    tenderLabel: tender.visibleLabel,
    tenderDetail: tender.visibleDetail
  };
}
