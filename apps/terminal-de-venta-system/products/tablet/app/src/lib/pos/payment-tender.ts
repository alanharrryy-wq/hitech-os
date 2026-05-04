import type { PaymentMethod } from "./payment-state";

export type CashTenderReview = {
  canContinue: boolean;
  missingCents: number;
  changeCents: number;
  visibleLabel: string;
  visibleDetail: string;
};

export function centsFromDecimalString(value: string) {
  const normalized = value.replace(/,/g, "").trim();
  const parsed = Number(normalized);
  if (!Number.isFinite(parsed) || parsed <= 0) return 0;
  return Math.round(parsed * 100);
}

export function reviewCashTender(method: PaymentMethod, totalCents: number, receivedCents: number): CashTenderReview {
  if (totalCents <= 0) return { canContinue: false, missingCents: 0, changeCents: 0, visibleLabel: "Ticket sin total", visibleDetail: "Agrega productos con precio para poder cobrar." };
  if (method !== "cash") return { canContinue: true, missingCents: 0, changeCents: 0, visibleLabel: "Pago listo para ticket", visibleDetail: "Confirma la operación en banco/terminal y después toca OK para generar ticket." };
  if (receivedCents <= 0) return { canContinue: false, missingCents: totalCents, changeCents: 0, visibleLabel: "Falta efectivo recibido", visibleDetail: "Selecciona billete/monedas o captura cuánto entregó el cliente." };
  if (receivedCents < totalCents) return { canContinue: false, missingCents: totalCents - receivedCents, changeCents: 0, visibleLabel: "Efectivo insuficiente", visibleDetail: "Todavía falta dinero para cubrir el total." };
  return {
    canContinue: true,
    missingCents: 0,
    changeCents: receivedCents - totalCents,
    visibleLabel: receivedCents === totalCents ? "Pago exacto" : "Cambio calculado",
    visibleDetail: receivedCents === totalCents ? "No hay cambio por entregar. Toca OK para generar ticket." : "Entrega el cambio al cliente y toca OK para generar ticket."
  };
}

export function suggestedCashTenderCents(totalCents: number) {
  const nextPeso = Math.ceil(totalCents / 100) * 100;
  const commonDenominations = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000];
  const roundedDenominations = commonDenominations.filter((value) => value >= totalCents);
  return [totalCents, nextPeso, ...roundedDenominations].filter((value, index, array) => value >= totalCents && array.indexOf(value) === index).slice(0, 6);
}
