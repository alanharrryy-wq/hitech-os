export function catalogVisibleError(error: unknown) {
  if (!error) return "No se pudo completar la operación.";
  if (typeof error === "string") return error;
  if (error instanceof Error) return error.message;
  if (typeof error === "object" && "message" in error) {
    const payload = error as { code?: string; message?: string };
    const known: Record<string, string> = {
      DUPLICATE_SKU: "Ya existe un producto con ese SKU.",
      DUPLICATE_BARCODE: "Ese código de barras ya pertenece a otro producto.",
      INVALID_PRODUCT_PRICE: "El precio debe ser mayor a cero.",
      PRODUCT_NOT_FOUND: "No encontramos ese producto."
    };
    if (payload.code && known[payload.code]) return known[payload.code];
    if (payload.message) return payload.message;
  }
  return "No se pudo completar la operación.";
}
