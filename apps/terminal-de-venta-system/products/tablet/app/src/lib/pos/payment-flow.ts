
import type { CartLine, CompletedSaleReceipt } from "./cart-state";
import { requestJson } from "./cart-state";
import { buildCheckoutPayload } from "./cart-engine";
import type { PaymentMethod, PaymentTenderInput } from "./payment-state";
import { normalizePaymentMethod, normalizePaymentTenders } from "./payment-state";
import { resolvePaymentSessionContext } from "./payment-session";
import { buildPaymentReviewViewModel } from "./payment-view-model";

export async function completeCartSale(input: {
  lines: CartLine[];
  paymentMethod?: PaymentMethod;
  cashReceivedCents?: number;
  paymentTenders?: PaymentTenderInput[];
  clientRequestId: string;
}): Promise<CompletedSaleReceipt> {
  const session = resolvePaymentSessionContext(input.lines);
  const checkout = buildCheckoutPayload({
    lines: input.lines,
    terminalId: session.terminalId,
    cashier: session.cashier,
    clientRequestId: input.clientRequestId
  });
  if (!checkout.ready) throw new Error(checkout.reason);
  const legacyMethod = input.paymentMethod ? normalizePaymentMethod(input.paymentMethod) : null;
  const paymentTenders = normalizePaymentTenders(
    input.paymentTenders ?? (legacyMethod ? [{ id: legacyMethod, method: legacyMethod, amountCents: legacyMethod === "cash" ? input.cashReceivedCents ?? 0 : checkout.totalCents, reference: "" }] : undefined)
  );

  const review = buildPaymentReviewViewModel({ lines: input.lines, paymentTenders });
  if (!review.canConfirm) throw new Error(review.blockReason ?? review.tenderDetail);
  const payloadTenders = review.tenders.map((tender) => ({
    tenderType: tender.method,
    amountCents: tender.amountCents,
    reference: tender.reference.trim() || null
  }));

  const payload = {
    ...session,
    businessId: checkout.businessId ?? session.businessId,
    terminalId: checkout.terminalId,
    cashier: checkout.cashier,
    clientRequestId: input.clientRequestId,
    paymentMethod: review.paymentMethod,
    cashReceivedCents: review.cashReceivedCents,
    changeCents: review.changeCents,
    paymentTenders: payloadTenders,
    items: checkout.items
  };

  async function postSale() {
    return requestJson<{ sale: CompletedSaleReceipt }>("/api/pos/sales/complete", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  const response = await postSale();

  return {
    ...response.data.sale,
    paymentMethod: review.paymentMethod,
    cashReceivedCents: review.cashReceivedCents,
    changeCents: review.changeCents,
    paymentTenders: response.data.sale.paymentTenders ?? response.data.sale.ticketEvidence?.payment.tenders ?? payloadTenders,
    clientRequestId: input.clientRequestId
  };
}
