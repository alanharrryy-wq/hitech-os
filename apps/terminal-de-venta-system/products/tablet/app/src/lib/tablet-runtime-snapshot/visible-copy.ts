export const TABLET_RUNTIME_VISIBLE_COPY = {
  shift: {
    open: "Turno abierto",
    closed: "Turno cerrado",
    closing: "Cerrando turno",
    review: "Revisar turno"
  },
  connection: {
    online: "En linea",
    offline: "Sin conexion",
    pending: "Pendientes por enviar",
    review: "Revisar pendientes"
  },
  catalog: {
    ready: "Catalogo listo",
    empty: "Catalogo vacio",
    stale: "Revisar catalogo",
    review: "Revisar existencias"
  },
  actions: {
    sell: "Ir a vender",
    openShift: "Abrir turno",
    reviewPending: "Ver pendientes",
    reviewStock: "Ver existencias",
    reviewCatalog: "Ver catalogo"
  }
} as const;

export const TABLET_RUNTIME_FORBIDDEN_VISIBLE_TERMS = [
  "outbox",
  "runtime",
  "payload",
  "schema",
  "mutation",
  "query",
  "lookup",
  "amountCents",
  "terminalId",
  "businessId",
  "undefined",
  "null",
  "NaN",
  "fatal"
] as const;

export function containsForbiddenVisibleTerm(value: string) {
  const lower = value.toLowerCase();
  return TABLET_RUNTIME_FORBIDDEN_VISIBLE_TERMS.find((term) => lower.includes(term.toLowerCase())) ?? null;
}
