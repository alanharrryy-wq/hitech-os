export type SupplierActionRecord = {
  id: string;
  kind: "simulation" | "order" | "receiving" | "payment" | "audit";
  status: "success" | "error";
  title: string;
  message: string;
  createdAt: string;
  details: Array<{ label: string; value: string }>;
  warnings: string[];
  auditEvents: Array<{ id: string; label: string; summary: string; actor: string; date: string }>;
  context: {
    recommendationId?: string;
    orderId?: string;
    payableId?: string;
    budgetPesos?: string;
    paymentPesos?: string;
    reason?: string;
  };
};

export type SupplierDraftState = {
  recommendationId: string;
  orderId: string;
  payableId: string;
  budgetPesos: string;
  paymentPesos: string;
  reason: string;
  updatedAt: string;
};

export type SupplierPersistenceState = {
  version: 10;
  updatedAt: string;
  draft?: SupplierDraftState;
  actions: SupplierActionRecord[];
};

const STORAGE_KEY = "prisma.pc.proveedores.persistencia.v10";
const MAX_ACTIONS = 40;

export function emptySupplierPersistence(): SupplierPersistenceState {
  return {
    version: 10,
    updatedAt: new Date(0).toISOString(),
    actions: []
  };
}

export function readSupplierPersistence(): SupplierPersistenceState {
  if (!canUseBrowserStorage()) return emptySupplierPersistence();

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptySupplierPersistence();

    const parsed = JSON.parse(raw) as Partial<SupplierPersistenceState>;
    if (parsed.version !== 10 || !Array.isArray(parsed.actions)) return emptySupplierPersistence();

    return {
      version: 10,
      updatedAt: typeof parsed.updatedAt === "string" ? parsed.updatedAt : new Date().toISOString(),
      draft: normalizeDraft(parsed.draft),
      actions: parsed.actions.slice(0, MAX_ACTIONS).map(normalizeAction).filter(Boolean) as SupplierActionRecord[]
    };
  } catch {
    return emptySupplierPersistence();
  }
}

export function writeSupplierPersistence(next: SupplierPersistenceState): SupplierPersistenceState {
  const state: SupplierPersistenceState = {
    version: 10,
    updatedAt: next.updatedAt || new Date().toISOString(),
    draft: normalizeDraft(next.draft),
    actions: next.actions.slice(0, MAX_ACTIONS).map(normalizeAction).filter(Boolean) as SupplierActionRecord[]
  };

  if (canUseBrowserStorage()) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  return state;
}

export function saveSupplierDraft(draft: Omit<SupplierDraftState, "updatedAt">): SupplierPersistenceState {
  const current = readSupplierPersistence();
  return writeSupplierPersistence({
    ...current,
    updatedAt: new Date().toISOString(),
    draft: {
      ...draft,
      updatedAt: new Date().toISOString()
    }
  });
}

export function appendSupplierActionRecord(record: SupplierActionRecord): SupplierPersistenceState {
  const current = readSupplierPersistence();
  return writeSupplierPersistence({
    ...current,
    updatedAt: record.createdAt,
    actions: [record, ...current.actions].slice(0, MAX_ACTIONS)
  });
}

export function clearSupplierPersistence(): SupplierPersistenceState {
  if (canUseBrowserStorage()) {
    window.localStorage.removeItem(STORAGE_KEY);
  }
  return emptySupplierPersistence();
}

export function supplierPersistenceFileName() {
  const stamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, "");
  return `prisma_proveedores_persistencia_${stamp}.json`;
}

function normalizeDraft(value: unknown): SupplierDraftState | undefined {
  if (!value || typeof value !== "object") return undefined;
  const draft = value as Partial<SupplierDraftState>;
  return {
    recommendationId: String(draft.recommendationId ?? ""),
    orderId: String(draft.orderId ?? ""),
    payableId: String(draft.payableId ?? ""),
    budgetPesos: String(draft.budgetPesos ?? ""),
    paymentPesos: String(draft.paymentPesos ?? ""),
    reason: String(draft.reason ?? ""),
    updatedAt: String(draft.updatedAt ?? new Date().toISOString())
  };
}

function normalizeAction(value: unknown): SupplierActionRecord | undefined {
  if (!value || typeof value !== "object") return undefined;
  const item = value as Partial<SupplierActionRecord>;
  if (item.status !== "success" && item.status !== "error") return undefined;

  return {
    id: String(item.id ?? `accion-${Date.now()}`),
    kind: isActionKind(item.kind) ? item.kind : "audit",
    status: item.status,
    title: String(item.title ?? "Acción registrada"),
    message: String(item.message ?? "Resultado guardado."),
    createdAt: String(item.createdAt ?? new Date().toISOString()),
    details: Array.isArray(item.details) ? item.details.map(normalizePair) : [],
    warnings: Array.isArray(item.warnings) ? item.warnings.map(String) : [],
    auditEvents: Array.isArray(item.auditEvents) ? item.auditEvents.map(normalizeAuditEvent) : [],
    context: typeof item.context === "object" && item.context ? item.context : {}
  };
}

function normalizePair(value: unknown) {
  const item = value as { label?: unknown; value?: unknown };
  return { label: String(item?.label ?? "Dato"), value: String(item?.value ?? "") };
}

function normalizeAuditEvent(value: unknown) {
  const item = value as { id?: unknown; label?: unknown; summary?: unknown; actor?: unknown; date?: unknown };
  return {
    id: String(item?.id ?? `evento-${Date.now()}`),
    label: String(item?.label ?? "Evento"),
    summary: String(item?.summary ?? "Rastro guardado."),
    actor: String(item?.actor ?? "PRISMA"),
    date: String(item?.date ?? "Fecha por revisar")
  };
}

function isActionKind(value: unknown): value is SupplierActionRecord["kind"] {
  return value === "simulation" || value === "order" || value === "receiving" || value === "payment" || value === "audit";
}

function canUseBrowserStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}
