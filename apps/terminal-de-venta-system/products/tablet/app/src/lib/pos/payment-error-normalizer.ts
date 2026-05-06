export type PosVisibleErrorCode =
  | "EMPTY_CART"
  | "INVALID_QUANTITY"
  | "PRODUCT_NOT_FOUND"
  | "PRODUCT_INACTIVE"
  | "INSUFFICIENT_STOCK"
  | "TERMINAL_NOT_FOUND"
  | "NETWORK_UNAVAILABLE"
  | "SYNC_PENDING"
  | "DUPLICATE_REQUEST"
  | "UNKNOWN";

export type PosVisibleError = {
  code: PosVisibleErrorCode;
  title: string;
  message: string;
  operatorAction: string;
  canRetry: boolean;
  severity: "warning" | "danger";
};

const ERROR_COPY: Record<PosVisibleErrorCode, Omit<PosVisibleError, "code">> = {
  EMPTY_CART: { title: "Ticket vacío", message: "Agrega al menos un producto antes de cobrar.", operatorAction: "Busca o escanea un producto y vuelve a intentar.", canRetry: false, severity: "warning" },
  INVALID_QUANTITY: { title: "Cantidad inválida", message: "Una línea del ticket tiene una cantidad que no se puede cobrar.", operatorAction: "Revisa cantidades y elimina líneas dudosas.", canRetry: false, severity: "warning" },
  PRODUCT_NOT_FOUND: { title: "Producto no encontrado", message: "El producto ya no existe o no está disponible en la base local.", operatorAction: "Busca el producto por nombre o revisa catálogo.", canRetry: true, severity: "warning" },
  PRODUCT_INACTIVE: { title: "Producto inactivo", message: "Este producto no está habilitado para venta.", operatorAction: "Quita el producto del ticket o pide revisión en PC.", canRetry: false, severity: "danger" },
  INSUFFICIENT_STOCK: { title: "Stock insuficiente", message: "No hay piezas suficientes para cerrar esta venta.", operatorAction: "Reduce la cantidad o revisa existencias.", canRetry: true, severity: "warning" },
  TERMINAL_NOT_FOUND: { title: "Terminal no configurada", message: "Esta Tablet no tiene una terminal local válida.", operatorAction: "No cierres ventas hasta revisar configuración.", canRetry: false, severity: "danger" },
  NETWORK_UNAVAILABLE: { title: "Sin conexión", message: "La conexión no respondió. Si la venta es local, puede quedar pendiente de envío.", operatorAction: "Revisa el estado de pendientes antes de repetir el cobro.", canRetry: true, severity: "warning" },
  SYNC_PENDING: { title: "Venta guardada localmente", message: "La venta quedó registrada y falta enviarla cuando haya conexión.", operatorAction: "Puedes seguir operando y revisar Pendientes más tarde.", canRetry: false, severity: "warning" },
  DUPLICATE_REQUEST: { title: "Cobro ya procesado", message: "Esta solicitud ya fue usada para evitar doble venta.", operatorAction: "Revisa el ticket cerrado o inicia una nueva venta.", canRetry: false, severity: "warning" },
  UNKNOWN: { title: "No se pudo cerrar", message: "La venta no se pudo confirmar con seguridad.", operatorAction: "No repitas el cobro sin revisar el estado del ticket.", canRetry: true, severity: "danger" },
};

export function normalizePosError(error: unknown): PosVisibleError {
  const raw = typeof error === "string" ? error : error instanceof Error ? error.message : JSON.stringify(error ?? "");
  const upper = raw.toUpperCase();
  const known = (Object.keys(ERROR_COPY) as PosVisibleErrorCode[]).find(code => upper.includes(code));
  const code = known ?? (upper.includes("FETCH") || upper.includes("NETWORK") ? "NETWORK_UNAVAILABLE" : "UNKNOWN");
  return { code, ...ERROR_COPY[code] };
}

export function visibleErrorFromApiPayload(payload: unknown): PosVisibleError {
  if (!payload || typeof payload !== "object") return normalizePosError(payload);
  const code = "code" in payload ? String((payload as { code?: unknown }).code ?? "UNKNOWN") : "UNKNOWN";
  return normalizePosError(code);
}
