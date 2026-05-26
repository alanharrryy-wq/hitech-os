// PRISMA PC UIUX V02 copy dictionary.
// Human language outside, technical evidence inside.

export const PC_STATUS_COPY = {
  live: "Actualizado",
  healthy: "Bien",
  ok: "Bien",
  success: "Completado",
  warning: "Requiere atención",
  stale: "Atrasado",
  degraded: "Con problemas",
  partial: "Incompleto",
  critical: "Crítico",
  error: "Con error",
  failed: "Falló",
  blocking: "Bloqueado",
  offline: "Sin conexión",
  mock: "Demo",
  demo: "Demo",
  pending: "Pendiente",
  queued: "En espera",
  loading: "Preparando información",
  real: "Datos reales",
  hybrid: "Datos mixtos",
  static: "Referencia estática",
  high: "Alta",
  medium: "Media",
  low: "Baja",
  missing: "Sin lectura suficiente",
  blocked: "Lectura bloqueada",
  proxy: "Estimación operativa"
} as const;

export const PC_TERM_COPY = {
  runtime: "Sistema",
  ingest: "Recepción de cambios",
  payload: "Paquete de datos",
  ack: "Confirmación",
  dispatcher: "Envío de cambios",
  canonical: "Base principal",
  "canonical db": "Base principal",
  db: "Base",
  database: "Base de datos",
  sqlite: "Base local",
  "feature gate": "Función disponible",
  raw: "Detalle técnico",
  adapter: "Conector",
  registry: "Registro interno",
  manifest: "Resumen técnico",
  "tri-db": "Sincronización entre equipos",
  delta: "Cambios nuevos",
  endpoint: "Ruta técnica",
  debug: "Diagnóstico",
  hydration: "Carga de interfaz",
  audit: "Historial",
  devices: "Equipos",
  "data quality": "Revisión de datos",
  "tablet communication": "Tablet",
  "license runtime": "Licencia"
} as const;

export const PC_EMPTY_STATE_COPY = {
  defaultTitle: "No hay pendientes",
  defaultBody: "Todo está dentro del rango esperado. Puedes revisar el detalle o descargar el reporte si necesitas evidencia.",
  defaultAction: "Ver detalle"
} as const;

export const PC_ERROR_STATE_COPY = {
  defaultTitle: "No se pudo cargar esta información",
  defaultBody: "El sistema no pudo leer la información necesaria para esta pantalla.",
  defaultRecovery: "Reintenta. Si continúa, abre la evidencia técnica para ver la causa exacta.",
  defaultAction: "Reintentar"
} as const;

export function translatePcStatus(status: string): string {
  const key = status.toLowerCase().trim() as keyof typeof PC_STATUS_COPY;
  return PC_STATUS_COPY[key] ?? status;
}

export function translatePcTerm(term: string): string {
  const key = term.toLowerCase().trim() as keyof typeof PC_TERM_COPY;
  return PC_TERM_COPY[key] ?? term;
}
