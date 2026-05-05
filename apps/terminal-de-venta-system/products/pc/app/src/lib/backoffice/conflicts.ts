export type ConflictCode =
  | "product_discontinued"
  | "old_local_price"
  | "negative_stock"
  | "duplicate_event"
  | "terminal_not_registered"
  | "sale_outside_shift"
  | "inconsistent_sequence"
  | "invalid_schema"
  | "unknown_topic";

export type ConflictSeverity = "warning" | "conflict" | "rejected";

export type ConflictFinding = {
  code: ConflictCode;
  label: string;
  severity: ConflictSeverity;
  detail: string;
};

export const CONFLICT_CATALOG: Record<ConflictCode, Omit<ConflictFinding, "detail">> = {
  product_discontinued: {
    code: "product_discontinued",
    label: "Producto descontinuado",
    severity: "conflict"
  },
  old_local_price: {
    code: "old_local_price",
    label: "Precio local desactualizado",
    severity: "conflict"
  },
  negative_stock: {
    code: "negative_stock",
    label: "Stock negativo",
    severity: "conflict"
  },
  duplicate_event: {
    code: "duplicate_event",
    label: "Evento duplicado",
    severity: "warning"
  },
  terminal_not_registered: {
    code: "terminal_not_registered",
    label: "Terminal no registrada",
    severity: "conflict"
  },
  sale_outside_shift: {
    code: "sale_outside_shift",
    label: "Venta fuera de turno",
    severity: "conflict"
  },
  inconsistent_sequence: {
    code: "inconsistent_sequence",
    label: "Secuencia inconsistente",
    severity: "conflict"
  },
  invalid_schema: {
    code: "invalid_schema",
    label: "Schema inválido",
    severity: "rejected"
  },
  unknown_topic: {
    code: "unknown_topic",
    label: "Tópico desconocido",
    severity: "rejected"
  }
};

export function conflictFinding(code: ConflictCode, detail: string): ConflictFinding {
  return { ...CONFLICT_CATALOG[code], detail };
}

export function getConflictCatalog() {
  return Object.values(CONFLICT_CATALOG).map((item) => ({
    ...item,
    detail: "Clasificador preparado para validación determinista de eventos Tablet."
  }));
}
