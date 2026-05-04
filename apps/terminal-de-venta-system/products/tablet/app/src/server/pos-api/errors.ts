import { PosEngineError } from "../pos-engine/errors";
import { fail } from "./responses";

const POS_ENGINE_HTTP_STATUS: Record<string, number> = {
  EMPTY_CART: 400,
  INVALID_QUANTITY: 400,
  PRODUCT_NOT_FOUND: 404,
  PRODUCT_INACTIVE: 409,
  INSUFFICIENT_STOCK: 409,
  TERMINAL_NOT_FOUND: 409,
  SHIFT_NOT_OPEN: 409,
  NETWORK_UNAVAILABLE: 503,
  SYNC_PENDING: 202,
  BUSINESS_NOT_FOUND: 409,
  ENGINE_INVARIANT_FAILED: 500
};

const POS_ENGINE_PUBLIC_MESSAGE: Record<string, string> = {
  EMPTY_CART: "El carrito esta vacio; agrega productos antes de cerrar la venta.",
  INVALID_QUANTITY: "La cantidad debe ser un numero entero mayor a cero.",
  PRODUCT_NOT_FOUND: "Producto no encontrado en el catalogo local de Tablet.",
  PRODUCT_INACTIVE: "Producto inactivo; no puede venderse desde Tablet.",
  INSUFFICIENT_STOCK: "Stock insuficiente para cerrar la venta local.",
  TERMINAL_NOT_FOUND: "No hay terminal local activa para cerrar la venta.",
  SHIFT_NOT_OPEN: "Abre turno antes de cerrar ventas en esta terminal.",
  NETWORK_UNAVAILABLE: "La red no esta disponible; la venta local puede continuar si la regla lo permite.",
  SYNC_PENDING: "La sincronizacion queda pendiente; la operacion local fue registrada.",
  BUSINESS_NOT_FOUND: "No hay negocio local configurado para cerrar la venta.",
  ENGINE_INVARIANT_FAILED: "El motor POS detecto una inconsistencia interna."
};

export function toPosApiError(error: unknown) {
  if (error instanceof PosEngineError) {
    const status = POS_ENGINE_HTTP_STATUS[error.code] ?? 400;
    const message = POS_ENGINE_PUBLIC_MESSAGE[error.code] ?? error.message;
    return fail(error.code, message, status, error.details);
  }

  if (error instanceof Error) {
    return fail("POS_API_INTERNAL_ERROR", "Error interno al ejecutar la operacion POS local.", 500, {
      name: error.name,
      message: error.message
    });
  }

  return fail("POS_API_UNKNOWN_ERROR", "Error desconocido al ejecutar la operacion POS local.", 500);
}
