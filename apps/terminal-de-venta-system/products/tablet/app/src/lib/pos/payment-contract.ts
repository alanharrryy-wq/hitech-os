
export type CheckoutState = "idle" | "review" | "submitting" | "success" | "error";

export function isCheckoutBusy(state: CheckoutState) {
  return state === "submitting";
}

export function checkoutStateCopy(state: CheckoutState) {
  if (state === "success") return { label: "Ticket cerrado" };
  if (state === "submitting") return { label: "Cerrando venta" };
  if (state === "review") return { label: "Revisando cobro" };
  if (state === "error") return { label: "Revisar cobro" };
  return { label: "Venta local activa" };
}

export function checkoutStateTone(state: CheckoutState) {
  if (state === "error") return "danger";
  if (state === "review" || state === "submitting") return "warn";
  return "ok";
}
