
import type { CartLine, CompletedSaleReceipt } from "./cart-state";
import { requestJson } from "./cart-state";
import { buildCheckoutPayload } from "./cart-engine";
import type { PaymentMethod } from "./payment-state";
import { normalizePaymentMethod } from "./payment-state";
import { resolvePaymentSessionContext } from "./payment-session";
import { reviewCashTender } from "./payment-tender";
import { apiErrorCode, ensureLocalShiftOpenForSale } from "./shift-flow";

export async function completeCartSale(input: {
  lines: CartLine[];
  paymentMethod: PaymentMethod;
  cashReceivedCents: number;
  clientRequestId: string;
}): Promise<CompletedSaleReceipt> {
  const paymentMethod = normalizePaymentMethod(input.paymentMethod);
  const session = resolvePaymentSessionContext(input.lines);
  const checkout = buildCheckoutPayload({
    lines: input.lines,
    terminalId: session.terminalId,
    cashier: session.cashier,
    clientRequestId: input.clientRequestId,
    paymentMethod,
    cashReceivedCents: input.cashReceivedCents
  });
  if (!checkout.ready) throw new Error(checkout.reason);

  const tender = reviewCashTender(paymentMethod, checkout.totalCents, input.cashReceivedCents);
  if (!tender.canContinue) throw new Error(tender.visibleDetail);

  const payload = {
    ...session,
    businessId: checkout.businessId ?? session.businessId,
    terminalId: checkout.terminalId,
    cashier: checkout.cashier,
    clientRequestId: input.clientRequestId,
    paymentMethod,
    cashReceivedCents: paymentMethod === "cash" ? input.cashReceivedCents : null,
    changeCents: tender.changeCents,
    items: checkout.items
  };

  async function postSale() {
    return requestJson<{ sale: CompletedSaleReceipt }>("/api/pos/sales/complete", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  let response: Awaited<ReturnType<typeof postSale>>;
  try {
    response = await postSale();
  } catch (error) {
    if (apiErrorCode(error) !== "SHIFT_NOT_OPEN") throw error;
    await ensureLocalShiftOpenForSale();
    response = await postSale();
  }

  return {
    ...response.data.sale,
    paymentMethod,
    cashReceivedCents: paymentMethod === "cash" ? input.cashReceivedCents : undefined,
    changeCents: tender.changeCents,
    clientRequestId: input.clientRequestId
  };
}
