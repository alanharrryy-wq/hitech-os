import type { ApiFail } from "./cart-state";

const ERROR_MESSAGES: Record<string, string> = {
  EMPTY_CART: "Agrega productos para poder cobrar.",
  INVALID_QUANTITY: "La cantidad no es válida.",
  PRODUCT_NOT_FOUND: "No encontramos ese producto.",
  PRODUCT_INACTIVE: "Este producto está inactivo y no puede venderse.",
  INSUFFICIENT_STOCK: "Existencias insuficientes para este producto.",
  SHIFT_NOT_OPEN: "No había caja abierta. PRISMA intentó abrir la caja local antes de generar ticket; si persiste, abre turno desde Caja.",
  TERMINAL_NOT_FOUND: "No se encontró la terminal configurada.",
  NETWORK_UNAVAILABLE: "No hay conexión disponible. La venta local puede continuar si el modo lo permite.",
  SYNC_PENDING: "Hay operaciones pendientes por enviar.",
  BUSINESS_NOT_FOUND: "No hay negocio local configurado para vender.",
  ENGINE_INVARIANT_FAILED: "El motor detectó una inconsistencia y no cerró la venta.",
  CASH_RECEIVED_REQUIRED: "Captura cuánto efectivo recibió la caja antes de generar ticket.",
  INVALID_PAYMENT_METHOD: "Selecciona un método de pago válido.",
  INVALID_PAYMENT_AMOUNT: "El monto recibido no es válido.",
  PRODUCT_REF_REQUIRED: "El ticket llego sin referencia de producto. Vuelve al ticket y reintenta.",
  POS_API_HTTP_ERROR: "El punto de venta local no respondio correctamente. Revisa que Tablet siga levantada antes de repetir el cobro.",
  POS_API_INVALID_RESPONSE: "El punto de venta respondio en un formato inesperado. No repitas el cobro sin revisar ventas de hoy.",
  POS_API_INTERNAL_ERROR: "El motor local no pudo cerrar la venta. Revisa consola o log antes de repetir el cobro.",
  POS_API_UNKNOWN_ERROR: "La venta no se pudo confirmar con seguridad. No repitas el cobro sin revisar ventas de hoy."
};

export function friendlyPosError(error: unknown) {
  if (!error) return "Ocurrió un problema al procesar la operación.";
  if (typeof error === "string") return ERROR_MESSAGES[error] ?? error;
  if (typeof error === "object" && "code" in error) {
    const apiError = error as ApiFail;
    return ERROR_MESSAGES[apiError.code] ?? apiError.message ?? "Ocurrió un problema al procesar la operación.";
  }
  if (typeof error === "object" && "message" in error) {
    return String((error as { message?: unknown }).message ?? "Ocurrió un problema al procesar la operación.");
  }
  if (error instanceof Error) return error.message;
  return "Ocurrió un problema al procesar la operación.";
}
