import type { SyncConflictFinding, SyncEventEnvelope, SyncLifecycleState } from "@/server/validators/sync-event-contract";

type TxClient = any;

type ProjectionStatus = Extract<SyncLifecycleState, "projected" | "reconciled" | "conflict" | "dead_letter">;

export type SyncProjectionResult = {
  status: ProjectionStatus;
  conflicts: SyncConflictFinding[];
  diagnostics: string[];
  touchedModels: string[];
};

function conflict(code: string, detail: string, severity: SyncConflictFinding["severity"] = "conflict"): SyncConflictFinding {
  const labels: Record<string, string> = {
    duplicate_event: "Evento duplicado",
    negative_stock: "Stock negativo",
    terminal_not_registered: "Terminal no registrada",
    sale_outside_shift: "Venta fuera de turno",
    inconsistent_sequence: "Secuencia inconsistente",
    invalid_schema: "Schema invalido",
    unknown_topic: "Topic desconocido",
    product_discontinued: "Producto no disponible"
  };
  return { code, label: labels[code] ?? code, severity, detail };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function asOptionalString(value: unknown) {
  const text = asString(value);
  return text || null;
}

function asInt(value: unknown) {
  if (Number.isInteger(value)) return value as number;
  if (typeof value === "number" && Number.isFinite(value)) return Math.trunc(value);
  if (typeof value === "string" && value.trim() && Number.isInteger(Number(value))) return Number(value);
  return null;
}

function asDate(value: unknown, fallback: string) {
  const text = asString(value) || fallback;
  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? new Date(fallback) : date;
}

function unsupported(event: SyncEventEnvelope): SyncProjectionResult {
  return {
    status: "dead_letter",
    conflicts: [conflict("unknown_topic", `No Prisma projector is registered for ${event.topic}.`, "rejected")],
    diagnostics: [`UNSUPPORTED_PROJECTOR:${event.topic}`],
    touchedModels: ["OutboxEvent"]
  };
}

async function ensureBusinessAndTerminal(tx: TxClient, event: SyncEventEnvelope): Promise<SyncConflictFinding[]> {
  const [business, terminal] = await Promise.all([
    tx.business.findUnique({ where: { id: event.businessId } }),
    tx.terminal.findFirst({ where: { id: event.terminalId, businessId: event.businessId, isActive: true } })
  ]);
  const conflicts: SyncConflictFinding[] = [];
  if (!business) conflicts.push(conflict("invalid_schema", `Business ${event.businessId} does not exist in canonical Prisma DB.`, "rejected"));
  if (!terminal) conflicts.push(conflict("terminal_not_registered", `Terminal ${event.terminalId} is not registered for business ${event.businessId}.`));
  return conflicts;
}

async function projectSaleCompleted(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["SALE_PROJECTOR_PRECONDITION_FAILED"], touchedModels: ["Sale"] };

  const payload = event.payload;
  const saleId = asString(payload.saleId) || event.aggregateId || event.eventId;
  const totalCents = asInt(payload.totalCents);
  const folio = asString(payload.folio) || saleId;
  const cashier = asString(payload.cashier) || event.actorId;
  if (!saleId || totalCents === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "sale.completed requires saleId and totalCents.", "rejected")], diagnostics: ["SALE_PAYLOAD_INCOMPLETE"], touchedModels: ["Sale"] };
  }

  const existing = await tx.sale.findFirst({ where: { id: saleId, businessId: event.businessId }, include: { lines: true } });
  if (existing) {
    if (existing.totalCents !== totalCents || existing.folio !== folio) {
      return {
        status: "conflict",
        conflicts: [conflict("duplicate_event", `Sale ${saleId} already exists with different folio or total.`)],
        diagnostics: ["SALE_DUPLICATE_MISMATCH"],
        touchedModels: ["Sale"]
      };
    }
    return { status: "reconciled", conflicts: [], diagnostics: ["SALE_ALREADY_PROJECTED"], touchedModels: ["Sale"] };
  }

  const cashSessionId = asOptionalString(payload.cashSessionId);
  if (cashSessionId) {
    const cashSession = await tx.cashSession.findFirst({ where: { id: cashSessionId, businessId: event.businessId } });
    if (!cashSession) {
      return {
        status: "conflict",
        conflicts: [conflict("sale_outside_shift", `CashSession ${cashSessionId} is missing for sale ${saleId}.`)],
        diagnostics: ["SALE_CASH_SESSION_MISSING"],
        touchedModels: ["Sale", "CashSession"]
      };
    }
  }

  const lines = Array.isArray(payload.lines) ? payload.lines.filter(isRecord) : [];
  const linePlans = [];
  for (const [index, line] of lines.entries()) {
    const productId = asString(line.productId);
    const qty = asInt(line.qty);
    const priceCents = asInt(line.priceCents);
    const lineTotalCents = asInt(line.totalCents);
    if (!productId || qty === null || priceCents === null || lineTotalCents === null) continue;
    const product = await tx.product.findFirst({ where: { id: productId, businessId: event.businessId } });
    if (!product) {
      return {
        status: "conflict",
        conflicts: [conflict("product_discontinued", `Product ${productId} is missing for projected SaleLine.`)],
        diagnostics: ["SALE_LINE_PRODUCT_MISSING"],
        touchedModels: ["Sale", "SaleLine", "Product"]
      };
    }
    linePlans.push({ index, line, product, productId, qty, priceCents, lineTotalCents });
  }

  await tx.sale.create({
    data: {
      id: saleId,
      businessId: event.businessId,
      terminalId: event.terminalId,
      cashSessionId,
      folio,
      cashier,
      totalCents,
      status: asString(payload.status) || "COMPLETED",
      createdAt: asDate(payload.createdAt, event.occurredAt)
    }
  });

  const touchedModels = ["Sale"];
  for (const { index, line, product, productId, qty, priceCents, lineTotalCents } of linePlans) {
    await tx.saleLine.create({
      data: {
        id: asString(line.id) || `${event.eventId}_line_${index + 1}`,
        businessId: event.businessId,
        saleId,
        productId,
        sku: asString(line.sku) || product.sku,
        productName: asString(line.productName) || product.name,
        qty,
        priceCents,
        totalCents: lineTotalCents,
        createdAt: asDate(payload.createdAt, event.occurredAt)
      }
    });
    if (!touchedModels.includes("SaleLine")) touchedModels.push("SaleLine");
  }

  return { status: "projected", conflicts: [], diagnostics: linePlans.length ? ["SALE_PROJECTED_WITH_LINES"] : ["SALE_PROJECTED_WITHOUT_LINES"], touchedModels };
}

async function projectStockDecremented(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const productId = asString(payload.productId) || event.aggregateId;
  const qty = asInt(payload.qty);
  const stockAfter = asInt(payload.stockAfter);
  if (!productId || qty === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "stock.decremented requires productId and qty.", "rejected")], diagnostics: ["STOCK_PAYLOAD_INCOMPLETE"], touchedModels: ["StockMovement"] };
  }
  if (stockAfter !== null && stockAfter < 0) {
    return { status: "conflict", conflicts: [conflict("negative_stock", `stockAfter for ${productId} is ${stockAfter}.`)], diagnostics: ["STOCK_NEGATIVE_TRANSITION"], touchedModels: ["Product", "StockMovement"] };
  }
  const product = await tx.product.findFirst({ where: { id: productId, businessId: event.businessId } });
  if (!product) {
    return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${productId} is missing or not active in canonical DB.`)], diagnostics: ["STOCK_PRODUCT_MISSING"], touchedModels: ["Product", "StockMovement"] };
  }
  const existing = await tx.stockMovement.findUnique({ where: { id: event.eventId } }).catch(() => null);
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["STOCK_MOVEMENT_ALREADY_PROJECTED"], touchedModels: ["StockMovement"] };

  await tx.stockMovement.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      productId,
      movement: "SALE",
      qty: -Math.abs(qty),
      reason: "sale.completed",
      location: asString(payload.location) || "tablet-floor",
      createdAt: asDate(payload.createdAt ?? event.occurredAt, event.occurredAt)
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["STOCK_DECREMENT_PROJECTED"], touchedModels: ["StockMovement", "Product"] };
}

async function projectCashSessionOpened(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["CASH_SESSION_PRECONDITION_FAILED"], touchedModels: ["CashSession"] };

  const payload = event.payload;
  const cashSessionId = asString(payload.cashSessionId) || event.aggregateId;
  const cashStartCents = asInt(payload.cashStartCents ?? payload.amountCents) ?? 0;
  const terminal = await tx.terminal.findFirst({ where: { id: event.terminalId, businessId: event.businessId } });
  const existing = await tx.cashSession.findFirst({ where: { id: cashSessionId, businessId: event.businessId } });
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["CASH_SESSION_ALREADY_PROJECTED"], touchedModels: ["CashSession"] };

  const open = await tx.cashSession.findFirst({ where: { businessId: event.businessId, terminalId: event.terminalId, status: "OPEN" } });
  if (open && open.id !== cashSessionId) {
    return { status: "conflict", conflicts: [conflict("inconsistent_sequence", `Terminal ${event.terminalId} already has open CashSession ${open.id}.`)], diagnostics: ["CASH_SESSION_OVERLAP"], touchedModels: ["CashSession"] };
  }
  if (!terminal) {
    return { status: "conflict", conflicts: [conflict("terminal_not_registered", `Terminal ${event.terminalId} missing for cash session ${cashSessionId}.`)], diagnostics: ["CASH_TERMINAL_MISSING"], touchedModels: ["Terminal", "CashSession"] };
  }

  await tx.cashSession.create({
    data: {
      id: cashSessionId,
      businessId: event.businessId,
      storeId: terminal.storeId,
      terminalId: event.terminalId,
      cashierId: event.actorId,
      cashier: asString(payload.cashier) || event.actorId,
      openedAt: asDate(payload.openedAt, event.occurredAt),
      cashStartCents,
      status: "OPEN"
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["CASH_SESSION_OPENED_PROJECTED"], touchedModels: ["CashSession"] };
}

async function projectCashMovementRecorded(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const cashSessionId = asString(payload.cashSessionId) || event.aggregateId;
  const amountCents = asInt(payload.amountCents ?? payload.countedCashCents);
  if (!cashSessionId || amountCents === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "cash.movement.recorded requires cashSessionId and amountCents.", "rejected")], diagnostics: ["CASH_MOVEMENT_PAYLOAD_INCOMPLETE"], touchedModels: ["CashMovement"] };
  }
  const session = await tx.cashSession.findFirst({ where: { id: cashSessionId, businessId: event.businessId } });
  if (!session) {
    return { status: "conflict", conflicts: [conflict("sale_outside_shift", `CashSession ${cashSessionId} missing for cash movement.`)], diagnostics: ["CASH_MOVEMENT_SESSION_MISSING"], touchedModels: ["CashSession", "CashMovement"] };
  }
  const existing = await tx.cashMovement.findUnique({ where: { id: event.eventId } }).catch(() => null);
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["CASH_MOVEMENT_ALREADY_PROJECTED"], touchedModels: ["CashMovement"] };

  await tx.cashMovement.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      cashSessionId,
      movement: asString(payload.movement) || "RECORDED",
      amountCents,
      reason: asString(payload.reason) || event.topic,
      createdAt: asDate(payload.createdAt ?? payload.closedAt, event.occurredAt)
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["CASH_MOVEMENT_PROJECTED"], touchedModels: ["CashMovement"] };
}

async function projectLowStockDetected(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const productId = asString(payload.productId) || event.aggregateId;
  const stockAfter = asInt(payload.stockAfter);
  const threshold = asInt(payload.threshold) ?? 0;
  if (!productId || stockAfter === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "inventory.low_stock_detected requires productId and stockAfter.", "rejected")], diagnostics: ["LOW_STOCK_PAYLOAD_INCOMPLETE"], touchedModels: ["ReplenishmentSignal"] };
  }
  const product = await tx.product.findFirst({ where: { id: productId, businessId: event.businessId } });
  if (!product) {
    return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${productId} missing for low-stock signal.`)], diagnostics: ["LOW_STOCK_PRODUCT_MISSING"], touchedModels: ["Product", "ReplenishmentSignal"] };
  }
  const existing = await tx.replenishmentSignal.findUnique({ where: { id: event.eventId } }).catch(() => null);
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["LOW_STOCK_ALREADY_PROJECTED"], touchedModels: ["ReplenishmentSignal"] };

  await tx.replenishmentSignal.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      productId,
      location: asString(payload.location) || "tablet-floor",
      suggestedQty: Math.max(1, threshold - stockAfter),
      priority: stockAfter <= 0 ? "critical" : "reorder",
      createdAt: asDate(payload.createdAt, event.occurredAt)
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["LOW_STOCK_SIGNAL_PROJECTED"], touchedModels: ["ReplenishmentSignal", "Product"] };
}

export async function projectAcceptedSyncEvent(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  if (event.topic === "sale.completed") return projectSaleCompleted(tx, event);
  if (event.topic === "stock.decremented") return projectStockDecremented(tx, event);
  if (event.topic === "cash.session.opened" || event.topic === "shift.opened") return projectCashSessionOpened(tx, event);
  if (event.topic === "cash.movement.recorded" || event.topic === "shift.closed") return projectCashMovementRecorded(tx, event);
  if (event.topic === "inventory.low_stock_detected") return projectLowStockDetected(tx, event);
  return unsupported(event);
}
