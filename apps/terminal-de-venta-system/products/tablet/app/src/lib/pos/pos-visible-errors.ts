import type { ApiFail } from "./cart-state";

const ERROR_MESSAGES: Record<string, string> = {
  EMPTY_CART: "Agrega productos para poder cobrar.",
  INVALID_QUANTITY: "La cantidad no es válida.",
  PRODUCT_NOT_FOUND: "No encontramos ese producto.",
  PRODUCT_INACTIVE: "Este producto está inactivo y no puede venderse.",
  INSUFFICIENT_STOCK: "Existencias insuficientes para este producto.",
  TERMINAL_NOT_FOUND: "No se encontró la terminal configurada.",
  NETWORK_UNAVAILABLE: "No hay conexión disponible. La venta local puede continuar si el modo lo permite.",
  SYNC_PENDING: "Hay operaciones pendientes por enviar.",
  BUSINESS_NOT_FOUND: "No hay negocio local configurado para vender.",
  ENGINE_INVARIANT_FAILED: "El motor detectó una inconsistencia y no cerró la venta."
};

export function friendlyPosError(error: unknown) {
  if (!error) return "Ocurrió un problema al procesar la operación.";
  if (typeof error === "string") return ERROR_MESSAGES[error] ?? error;
  if (typeof error === "object" && "code" in error) {
    const apiError = error as ApiFail;
    return ERROR_MESSAGES[apiError.code] ?? apiError.message ?? "Ocurrió un problema al procesar la operación.";
  }
  if (error instanceof Error) return error.message;
  return "Ocurrió un problema al procesar la operación.";
}
