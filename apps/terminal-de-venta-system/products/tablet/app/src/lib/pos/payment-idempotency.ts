
import { makeClientRequestId, type CartLine } from "./cart-state";

const KEY = "prisma.tablet.pos.paymentRequest.v1";

export function clearPaymentRequestRecord() {
  if (typeof window !== "undefined") window.localStorage.removeItem(KEY);
}

export async function getOrCreatePaymentRequestId(lines: CartLine[]) {
  if (typeof window === "undefined") return makeClientRequestId();
  const signature = lines.map((line) => `${line.product.id}:${line.qty}:${line.product.priceCents}`).join("|");
  const raw = window.localStorage.getItem(KEY);
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as { sig?: string; id?: string };
      if (parsed.sig === signature && parsed.id) return parsed.id;
    } catch {
      window.localStorage.removeItem(KEY);
    }
  }
  const id = makeClientRequestId();
  window.localStorage.setItem(KEY, JSON.stringify({ sig: signature, id }));
  return id;
}
