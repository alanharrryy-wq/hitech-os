export function prismaMobileErrorMessage(error: unknown, fallback = "No se pudo completar la operación móvil."): string {
  if (error instanceof Error && error.message.trim().length > 0) return error.message;
  if (typeof error === "string" && error.trim().length > 0) return error;
  if (error && typeof error === "object") {
    try {
      const json = JSON.stringify(error);
      if (json && json !== "{}") return json;
    } catch {
      // Ignore circular structures and fall through to the generic object label.
    }
    const tag = Object.prototype.toString.call(error);
    return tag && tag !== "[object Object]" ? tag : fallback;
  }
  return fallback;
}
