import type { SyncConflictFinding, SyncEventEnvelope, SyncLifecycleState } from "@/server/validators/sync-event-contract";

type TxClient = any;

type ProjectionStatus = Extract<SyncLifecycleState, "projected" | "recognized_not_projected" | "reconciled" | "conflict" | "dead_letter">;

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
    product_discontinued: "Producto no disponible",
    old_local_price: "Precio local viejo"
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

function asBool(value: unknown, fallback = false) {
  if (value === true || value === "true" || value === "1") return true;
  if (value === false || value === "false" || value === "0") return false;
  return fallback;
}

function asDate(value: unknown, fallback: string) {
  const text = asString(value) || fallback;
  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? new Date(fallback) : date;
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function json(value: unknown) {
  try {
    return JSON.stringify(value);
  } catch {
    return JSON.stringify({ unserializable: true });
  }
}

function uniqueStrings(values: unknown[]): string[] {
  return [...new Set(values.map(asString).filter(Boolean))];
}

function lineAmountCents(line: Record<string, unknown>, qty: number) {
  return asInt(line.amountCents ?? line.totalCents) ?? ((asInt(line.unitPriceCents ?? line.priceCents) ?? 0) * qty);
}

function unsupported(event: SyncEventEnvelope): SyncProjectionResult {
  return {
    status: "recognized_not_projected",
    conflicts: [],
    diagnostics: [`RECOGNIZED_NOT_PROJECTED:${event.topic}`],
    touchedModels: ["OutboxEvent"]
  };
}

async function ensureBusinessAndTerminal(tx: TxClient, event: SyncEventEnvelope): Promise<SyncConflictFinding[]> {
  const [business, terminal] = await Promise.all([
    tx.business.findUnique({ where: { id: event.businessId } }),
    tx.terminal.findFirst({
      where: { id: event.terminalId, businessId: event.businessId, isActive: true },
      select: { id: true, storeId: true }
    })
  ]);
  const conflicts: SyncConflictFinding[] = [];
  if (!business) conflicts.push(conflict("invalid_schema", `Business ${event.businessId} does not exist in canonical Prisma DB.`, "rejected"));
  if (!terminal) {
    conflicts.push(conflict("terminal_not_registered", `Terminal ${event.terminalId} is not registered for business ${event.businessId}.`));
  } else if (terminal.storeId !== event.storeId) {
    conflicts.push(conflict("invalid_schema", `Store ${event.storeId} does not own terminal ${event.terminalId}; canonical store is ${terminal.storeId}.`, "rejected"));
  }
  return conflicts;
}

async function prepareSaleLinePlans(tx: TxClient, event: SyncEventEnvelope, payload: Record<string, unknown>) {
  const lines = Array.isArray(payload.lines) ? payload.lines.filter(isRecord) : [];
  const plans = [];
  for (const [index, line] of lines.entries()) {
    const productId = asString(line.productId);
    const qty = asInt(line.qty);
    const priceCents = asInt(line.priceCents ?? line.unitPriceCents);
    const totalCents = asInt(line.totalCents ?? line.amountCents) ?? ((priceCents ?? 0) * (qty ?? 0));
    if (!productId || qty === null || priceCents === null || totalCents === null) continue;
    const product = await tx.product.findFirst({
      where: { id: productId, businessId: event.businessId },
      select: { id: true, sku: true, name: true, priceCents: true }
    });
    if (!product) {
      return {
        ok: false as const,
        result: {
          status: "conflict" as ProjectionStatus,
          conflicts: [conflict("product_discontinued", `Product ${productId} is missing for projected SaleLine.`)],
          diagnostics: ["SALE_LINE_PRODUCT_MISSING"],
          touchedModels: ["Sale", "SaleLine", "Product"]
        }
      };
    }
    plans.push({ index, line, product, productId, qty, priceCents, totalCents });
  }
  return { ok: true as const, plans };
}

async function createSaleLinesFromPlans(tx: TxClient, event: SyncEventEnvelope, saleId: string, payload: Record<string, unknown>, touchedModels: string[], plans: Array<any>) {
  for (const { index, line, product, productId, qty, priceCents, totalCents } of plans) {
    const lineId = asString(line.id ?? line.saleLineId) || `${event.eventId}_line_${index + 1}`;
    const existingLine = await tx.saleLine.findUnique({ where: { id: lineId } }).catch(() => null);
    if (existingLine) continue;
    await tx.saleLine.create({
      data: {
        id: lineId,
        businessId: event.businessId,
        saleId,
        productId,
        sku: asString(line.sku) || product.sku,
        productName: asString(line.productName ?? line.name) || product.name,
        qty,
        priceCents,
        totalCents,
        createdAt: asDate(payload.createdAt, event.occurredAt)
      }
    });
    if (!touchedModels.includes("SaleLine")) touchedModels.push("SaleLine");
  }
}

async function createSalePaymentTenders(tx: TxClient, event: SyncEventEnvelope, saleId: string, payload: Record<string, unknown>, totalCents: number, touchedModels: string[]) {
  const rawTenders = Array.isArray(payload.tenders) ? payload.tenders.filter(isRecord) : [];
  const tenders = rawTenders.length
    ? rawTenders
    : [{ tenderType: asString(payload.paymentMethod) || "cash", amountCents: totalCents, reference: payload.paymentReference ?? null }];

  for (const [index, tender] of tenders.entries()) {
    const amountCents = asInt(tender.amountCents) ?? totalCents;
    if (amountCents <= 0) continue;
    const id = asString(tender.id) || `${event.eventId}_tender_${index + 1}`;
    const existing = await tx.salePaymentTender.findUnique({ where: { id } }).catch(() => null);
    if (existing) continue;
    await tx.salePaymentTender.create({
      data: {
        id,
        businessId: event.businessId,
        saleId,
        tenderType: asString(tender.tenderType ?? tender.paymentMethod) || asString(payload.paymentMethod) || "cash",
        amountCents,
        reference: asOptionalString(tender.reference ?? payload.paymentReference),
        metadataJson: json({
          sourceEventId: event.eventId,
          cashReceivedCents: asInt(payload.cashReceivedCents),
          changeCents: asInt(payload.changeCents),
          rawTender: tender
        }),
        recordedAt: asDate(payload.completedAt ?? payload.createdAt, event.occurredAt)
      }
    });
    if (!touchedModels.includes("SalePaymentTender")) touchedModels.push("SalePaymentTender");
  }
}

async function projectSaleCreated(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["SALE_CREATED_PRECONDITION_FAILED"], touchedModels: ["Sale"] };

  const payload = event.payload;
  const saleId = asString(payload.saleId) || event.aggregateId || event.eventId;
  const folio = asString(payload.folio) || saleId;
  const existing = await tx.sale.findFirst({ where: { id: saleId, businessId: event.businessId } });
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["SALE_CREATED_ALREADY_PROJECTED"], touchedModels: ["Sale"] };

  await tx.sale.create({
    data: {
      id: saleId,
      businessId: event.businessId,
      terminalId: event.terminalId,
      cashSessionId: asOptionalString(payload.cashSessionId),
      folio,
      cashier: asString(payload.cashier) || event.actorId,
      totalCents: asInt(payload.totalCents) ?? 0,
      status: asString(payload.status) || "CREATED",
      createdAt: asDate(payload.createdAt, event.occurredAt)
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["SALE_CREATED_PROJECTED_AS_DRAFT"], touchedModels: ["Sale"] };
}

async function projectCustomerCreated(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const customerId = asString(payload.retailCustomerId);
  const displayName = asString(payload.displayName);
  const version = asInt(payload.version);
  if (!customerId || !displayName || version === null || version < 1) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "customer.created requires retailCustomerId, displayName and version.", "rejected")], diagnostics: ["CUSTOMER_CREATE_PAYLOAD_INCOMPLETE"], touchedModels: ["Customer"] };
  }
  const existing = await tx.$queryRaw<Array<{ id: string; businessId: string; displayName: string; version: number }>>`
    SELECT "id", "businessId", "displayName", "version" FROM "Customer" WHERE "id" = ${customerId} LIMIT 1
  `;
  const prior = existing[0];
  if (prior && prior.businessId !== event.businessId) {
    return { status: "conflict", conflicts: [conflict("invalid_schema", `Customer ${customerId} belongs to another business scope.`, "rejected")], diagnostics: ["CUSTOMER_CREATE_SCOPE_CONFLICT"], touchedModels: ["Customer"] };
  }
  if (prior && (prior.displayName !== displayName || Number(prior.version) !== version)) {
    return { status: "conflict", conflicts: [conflict("duplicate_event", `Customer ${customerId} already exists with another version or name.`)], diagnostics: ["CUSTOMER_CREATE_DUPLICATE_CONFLICT"], touchedModels: ["Customer"] };
  }
  if (prior) return { status: "reconciled", conflicts: [], diagnostics: ["CUSTOMER_CREATE_ALREADY_PROJECTED"], touchedModels: ["Customer"] };
  const duplicateName = await tx.$queryRaw<Array<{ id: string }>>`
    SELECT "id" FROM "Customer"
    WHERE "businessId" = ${event.businessId} AND "isActive" = true AND LOWER("displayName") = LOWER(${displayName})
    LIMIT 1
  `;
  if (duplicateName[0]) {
    return { status: "conflict", conflicts: [conflict("duplicate_event", `Customer name ${displayName} already belongs to customer ${duplicateName[0].id}.`)], diagnostics: ["CUSTOMER_CREATE_NAME_COLLISION"], touchedModels: ["Customer"] };
  }
  const occurredAt = asDate(payload.updatedAt, event.occurredAt);
  await tx.$executeRaw`
    INSERT INTO "Customer" ("id", "businessId", "displayName", "creditCents", "isActive", "version", "sourceSurface", "createdAt", "updatedAt")
    VALUES (${customerId}, ${event.businessId}, ${displayName}, 0, true, ${version}, 'tablet', ${occurredAt}, ${occurredAt})
  `;
  await tx.auditEvent.create({ data: { id: `${event.eventId}_customer_audit`, businessId: event.businessId, actorId: null, topic: "customer.created", entityType: "Customer", entityId: customerId, summary: "Cliente mínimo creado desde Tablet.", afterJson: json({ id: customerId, displayName, version, source: "tablet" }), metadataJson: json({ sourceEventId: event.eventId, privacy: "minimal_pos_projection" }), createdAt: occurredAt } });
  return { status: "projected", conflicts: [], diagnostics: ["CUSTOMER_CREATE_PROJECTED"], touchedModels: ["Customer", "AuditEvent"] };
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

  const cashSessionId = asOptionalString(payload.cashSessionId);
  const saleCustomerId = asOptionalString(payload.saleCustomerId);
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

  const linePlans = await prepareSaleLinePlans(tx, event, payload);
  if (!linePlans.ok) return linePlans.result;

  const existing = await tx.sale.findFirst({ where: { id: saleId, businessId: event.businessId }, include: { lines: true, paymentTenders: true } });
  const touchedModels = ["Sale"];
  if (existing) {
    const status = asString(existing.status).toUpperCase();
    const canUpgradeDraft = ["CREATED", "PENDING", "OPEN"].includes(status) && existing.folio === folio;
    const alreadyProjected = existing.totalCents === totalCents && existing.folio === folio && ["COMPLETED", "PAID"].includes(status);
    if (!canUpgradeDraft && !alreadyProjected) {
      return {
        status: "conflict",
        conflicts: [conflict("duplicate_event", `Sale ${saleId} already exists with different folio, total or status.`)],
        diagnostics: ["SALE_DUPLICATE_MISMATCH"],
        touchedModels: ["Sale"]
      };
    }
    if (canUpgradeDraft) {
      await tx.sale.update({
        where: { id: saleId },
        data: {
          cashSessionId,
          customerId: saleCustomerId,
          cashier,
          totalCents,
          status: asString(payload.status) || "COMPLETED",
          createdAt: asDate(payload.createdAt, event.occurredAt)
        }
      });
    }
    await createSaleLinesFromPlans(tx, event, saleId, payload, touchedModels, linePlans.plans);
    await createSalePaymentTenders(tx, event, saleId, payload, totalCents, touchedModels);
    return { status: alreadyProjected ? "reconciled" : "projected", conflicts: [], diagnostics: [alreadyProjected ? "SALE_ALREADY_PROJECTED" : "SALE_DRAFT_COMPLETED"], touchedModels };
  }

  await tx.sale.create({
    data: {
      id: saleId,
      businessId: event.businessId,
      terminalId: event.terminalId,
      cashSessionId,
      customerId: saleCustomerId,
      folio,
      cashier,
      totalCents,
      status: asString(payload.status) || "COMPLETED",
      createdAt: asDate(payload.createdAt, event.occurredAt)
    }
  });

  await createSaleLinesFromPlans(tx, event, saleId, payload, touchedModels, linePlans.plans);
  await createSalePaymentTenders(tx, event, saleId, payload, totalCents, touchedModels);
  return { status: "projected", conflicts: [], diagnostics: touchedModels.includes("SaleLine") ? ["SALE_PROJECTED_WITH_LINES_AND_TENDER"] : ["SALE_PROJECTED_WITH_TENDER_ONLY"], touchedModels };
}

async function projectTicketClosed(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const saleId = asString(payload.saleId) || event.aggregateId;
  if (!saleId) return { status: "dead_letter", conflicts: [conflict("invalid_schema", "ticket.closed requires saleId.", "rejected")], diagnostics: ["TICKET_PAYLOAD_INCOMPLETE"], touchedModels: ["Sale"] };
  const sale = await tx.sale.findFirst({ where: { id: saleId, businessId: event.businessId } });
  if (!sale) return { status: "recognized_not_projected", conflicts: [], diagnostics: ["TICKET_CLOSE_WAITING_FOR_SALE_COMPLETED"], touchedModels: ["OutboxEvent"] };
  return { status: "reconciled", conflicts: [], diagnostics: ["TICKET_CLOSE_RECONCILED_WITH_SALE"], touchedModels: ["Sale"] };
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
  const product = await tx.product.findFirst({
    where: { id: productId, businessId: event.businessId },
    select: { id: true, stockOnHand: true }
  });
  if (!product) {
    return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${productId} is missing or not active in canonical DB.`)], diagnostics: ["STOCK_PRODUCT_MISSING"], touchedModels: ["Product", "StockMovement"] };
  }
  const existing = await tx.stockMovement.findUnique({ where: { id: event.eventId } }).catch(() => null);
  if (existing) return { status: "reconciled", conflicts: [], diagnostics: ["STOCK_MOVEMENT_ALREADY_PROJECTED"], touchedModels: ["StockMovement", "Product"] };

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
  if (stockAfter !== null) {
    await tx.product.update({ where: { id: productId }, data: { stockOnHand: stockAfter } });
  } else {
    await tx.product.update({ where: { id: productId }, data: { stockOnHand: { decrement: Math.abs(qty) } } });
  }
  return { status: "projected", conflicts: [], diagnostics: [stockAfter !== null ? "STOCK_DECREMENT_PROJECTED_WITH_SNAPSHOT" : "STOCK_DECREMENT_PROJECTED_WITH_DELTA"], touchedModels: ["StockMovement", "Product"] };
}

async function projectStockAdjusted(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const productId = asString(payload.productId) || event.aggregateId;
  const qtyInput = asInt(payload.qty ?? payload.delta ?? payload.adjustmentQty);
  const stockAfter = asInt(payload.stockAfter ?? payload.afterQty);
  if (!productId || (qtyInput === null && stockAfter === null)) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "stock.adjusted requires productId plus qty/delta or stockAfter.", "rejected")], diagnostics: ["STOCK_ADJUST_PAYLOAD_INCOMPLETE"], touchedModels: ["Product", "StockMovement"] };
  }
  const product = await tx.product.findFirst({ where: { id: productId, businessId: event.businessId }, select: { id: true, stockOnHand: true } });
  if (!product) return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${productId} missing for stock adjustment.`)], diagnostics: ["STOCK_ADJUST_PRODUCT_MISSING"], touchedModels: ["Product", "StockMovement"] };
  const delta = stockAfter !== null ? stockAfter - product.stockOnHand : qtyInput ?? 0;
  const after = stockAfter !== null ? stockAfter : product.stockOnHand + delta;
  if (after < 0) return { status: "conflict", conflicts: [conflict("negative_stock", `stock.adjusted would leave ${productId} at ${after}.`)], diagnostics: ["STOCK_ADJUST_NEGATIVE"], touchedModels: ["Product", "StockMovement"] };
  const movementId = event.eventId;
  const existing = await tx.stockMovement.findUnique({ where: { id: movementId } }).catch(() => null);
  if (!existing) {
    await tx.stockMovement.create({
      data: {
        id: movementId,
        businessId: event.businessId,
        productId,
        movement: "ADJUSTMENT",
        qty: delta,
        reason: asString(payload.reason) || event.topic,
        location: asString(payload.location) || "tablet-floor",
        createdAt: asDate(payload.createdAt, event.occurredAt)
      }
    });
  }
  await tx.product.update({ where: { id: productId }, data: { stockOnHand: after } });
  return { status: existing ? "reconciled" : "projected", conflicts: [], diagnostics: ["STOCK_ADJUSTMENT_PROJECTED"], touchedModels: ["Product", "StockMovement"] };
}

async function projectInventoryOperationRecorded(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const result = asRecord(payload.result);
  const operationId = asString(result.operationId) || event.aggregateId;
  const action = asString(payload.action || result.action);
  if (!operationId || !["adjust", "count", "receive"].includes(action)) {
    return {
      status: "dead_letter",
      conflicts: [conflict("invalid_schema", "inventory.operation.recorded requires operationId and action adjust/count/receive.", "rejected")],
      diagnostics: ["INVENTORY_OPERATION_PAYLOAD_INCOMPLETE"],
      touchedModels: ["AuditEvent"]
    };
  }
  const existing = await tx.auditEvent.findUnique({ where: { id: event.eventId } }).catch(() => null);
  if (existing) {
    return { status: "reconciled", conflicts: [], diagnostics: ["INVENTORY_OPERATION_ALREADY_PROJECTED"], touchedModels: ["AuditEvent"] };
  }
  const actor = event.actorId
    ? await tx.user.findFirst({ where: { id: event.actorId, businessId: event.businessId, status: "ACTIVE" }, select: { id: true } })
    : null;
  await tx.auditEvent.create({
    data: {
      id: event.eventId,
      businessId: event.businessId,
      actorId: actor?.id ?? null,
      topic: "inventory.operation.recorded",
      entityType: "inventory_operation",
      entityId: operationId,
      summary: `Operación de inventario ${action} recibida desde Tablet.`,
      afterJson: JSON.stringify(result),
      metadataJson: JSON.stringify({ sourceEventId: event.eventId, terminalId: event.terminalId, idempotencyKey: event.idempotencyKey, contract: asString(payload.contract) }),
      createdAt: asDate(result.createdAt, event.occurredAt)
    }
  });
  return { status: "projected", conflicts: [], diagnostics: ["INVENTORY_OPERATION_AUDIT_PROJECTED"], touchedModels: ["AuditEvent"] };
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
  const amountCents = asInt(payload.amountCents ?? payload.countedCashCents ?? payload.cashEndCents);
  if (!cashSessionId || amountCents === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "cash.movement.recorded/shift.closed requires cashSessionId and amountCents.", "rejected")], diagnostics: ["CASH_MOVEMENT_PAYLOAD_INCOMPLETE"], touchedModels: ["CashMovement"] };
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
      movement: asString(payload.movement) || (event.topic === "shift.closed" ? "CLOSE" : "RECORDED"),
      amountCents,
      reason: asString(payload.reason) || event.topic,
      createdAt: asDate(payload.createdAt ?? payload.closedAt, event.occurredAt)
    }
  });
  const touchedModels = ["CashMovement"];
  if (event.topic === "shift.closed") {
    await tx.cashSession.update({
      where: { id: cashSessionId },
      data: {
        closedAt: asDate(payload.closedAt ?? payload.createdAt, event.occurredAt),
        cashEndCents: amountCents,
        expectedCashCents: asInt(payload.expectedCashCents),
        varianceCents: asInt(payload.varianceCents),
        status: "CLOSED"
      }
    });
    touchedModels.push("CashSession");
  }
  return { status: "projected", conflicts: [], diagnostics: [event.topic === "shift.closed" ? "SHIFT_CLOSED_PROJECTED" : "CASH_MOVEMENT_PROJECTED"], touchedModels };
}

async function projectLowStockDetected(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const productId = asString(payload.productId) || event.aggregateId;
  const stockAfter = asInt(payload.stockAfter);
  const threshold = asInt(payload.threshold) ?? 0;
  if (!productId || stockAfter === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "inventory.low_stock_detected requires productId and stockAfter.", "rejected")], diagnostics: ["LOW_STOCK_PAYLOAD_INCOMPLETE"], touchedModels: ["ReplenishmentSignal"] };
  }
  const product = await tx.product.findFirst({
    where: { id: productId, businessId: event.businessId },
    select: { id: true }
  });
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

function productPayload(event: SyncEventEnvelope) {
  const payload = event.payload;
  const after = asRecord(payload.after);
  const source = Object.keys(after).length ? after : payload;
  return {
    productId: asString(source.productId ?? payload.productId) || event.aggregateId,
    sku: asString(source.sku),
    name: asString(source.name),
    category: asString(source.category) || "General",
    priceCents: asInt(source.priceCents),
    costCents: asInt(source.costCents) ?? 0,
    stockOnHand: asInt(source.stockOnHand),
    isActive: asBool(source.isActive, true),
    barcodes: uniqueStrings([source.barcode, payload.barcode, ...(Array.isArray(source.barcodes) ? source.barcodes : []), ...(Array.isArray(payload.barcodes) ? payload.barcodes : [])])
  };
}

async function replaceProductBarcodes(tx: TxClient, event: SyncEventEnvelope, productId: string, barcodes: string[]) {
  for (const code of barcodes) {
    const existing = await tx.barcode.findUnique({ where: { businessId_code: { businessId: event.businessId, code } } }).catch(() => null);
    if (existing && existing.productId !== productId) {
      return conflict("duplicate_event", `Barcode ${code} already belongs to another product (${existing.productId}).`);
    }
  }
  await tx.barcode.deleteMany({ where: { businessId: event.businessId, productId } });
  for (const code of barcodes) {
    await tx.barcode.create({
      data: {
        id: `${productId}_barcode_${code}`.slice(0, 120),
        businessId: event.businessId,
        productId,
        code
      }
    });
  }
  return null;
}

async function projectCatalogProduct(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["CATALOG_PRODUCT_PRECONDITION_FAILED"], touchedModels: ["Product"] };

  const data = productPayload(event);
  if (!data.productId || !data.sku || !data.name || data.priceCents === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "catalog.product.* requires productId, sku, name and priceCents.", "rejected")], diagnostics: ["CATALOG_PRODUCT_PAYLOAD_INCOMPLETE"], touchedModels: ["Product"] };
  }
  const bySku = await tx.product.findUnique({ where: { businessId_sku: { businessId: event.businessId, sku: data.sku } } }).catch(() => null);
  if (bySku && bySku.id !== data.productId) {
    return { status: "conflict", conflicts: [conflict("duplicate_event", `SKU ${data.sku} already belongs to product ${bySku.id}.`)], diagnostics: ["CATALOG_SKU_COLLISION"], touchedModels: ["Product"] };
  }
  const barcodeConflict = await replaceProductBarcodes(tx, event, data.productId, data.barcodes);
  if (barcodeConflict) return { status: "conflict", conflicts: [barcodeConflict], diagnostics: ["CATALOG_BARCODE_COLLISION"], touchedModels: ["Product", "Barcode"] };

  const existing = await tx.product.findFirst({ where: { id: data.productId, businessId: event.businessId } });
  const stockOnHand = data.stockOnHand ?? existing?.stockOnHand ?? 0;
  await tx.product.upsert({
    where: { id: data.productId },
    create: {
      id: data.productId,
      businessId: event.businessId,
      sku: data.sku,
      name: data.name,
      category: data.category,
      priceCents: data.priceCents,
      costCents: data.costCents,
      stockOnHand,
      isActive: data.isActive,
      createdAt: asDate(event.payload.createdAt, event.occurredAt)
    },
    update: {
      sku: data.sku,
      name: data.name,
      category: data.category,
      priceCents: data.priceCents,
      costCents: data.costCents,
      stockOnHand,
      isActive: data.isActive
    }
  });
  const touchedModels = ["Product"];
  if (data.barcodes.length) touchedModels.push("Barcode");
  return { status: existing ? "reconciled" : "projected", conflicts: [], diagnostics: [existing ? "CATALOG_PRODUCT_UPDATED" : "CATALOG_PRODUCT_CREATED"], touchedModels };
}

async function projectSaleRefunded(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const returnId = asString(payload.returnId ?? payload.saleReturnId) || event.aggregateId || event.eventId;
  const saleFolio = asString(payload.saleFolio ?? payload.folio);
  const amountCents = asInt(payload.amountCents);
  if (!returnId || !saleFolio || amountCents === null) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "sale.refunded requires returnId, saleFolio and amountCents.", "rejected")], diagnostics: ["RETURN_PAYLOAD_INCOMPLETE"], touchedModels: ["SaleReturn"] };
  }
  const existing = await tx.saleReturn.findFirst({ where: { id: returnId, businessId: event.businessId } });
  if (existing) {
    if (existing.amountCents !== amountCents) return { status: "conflict", conflicts: [conflict("duplicate_event", `SaleReturn ${returnId} exists with a different amount.`)], diagnostics: ["RETURN_DUPLICATE_MISMATCH"], touchedModels: ["SaleReturn"] };
    return { status: "reconciled", conflicts: [], diagnostics: ["RETURN_ALREADY_PROJECTED"], touchedModels: ["SaleReturn"] };
  }

  const sale = await tx.sale.findFirst({
    where: { businessId: event.businessId, OR: [{ id: asString(payload.saleId) || "__none__" }, { folio: saleFolio }] },
    include: { lines: true }
  }).catch(() => null);
  const lines = Array.isArray(payload.lines) ? payload.lines.filter(isRecord) : [];
  if (!lines.length) return { status: "dead_letter", conflicts: [conflict("invalid_schema", "sale.refunded requires at least one line.", "rejected")], diagnostics: ["RETURN_LINES_MISSING"], touchedModels: ["SaleReturn", "SaleReturnLine"] };

  const returnLinePlans = [];
  for (const [index, line] of lines.entries()) {
    const productId = asString(line.productId);
    const qty = asInt(line.qty);
    if (!productId || qty === null || qty <= 0) continue;
    const product = await tx.product.findFirst({ where: { id: productId, businessId: event.businessId }, select: { id: true, sku: true, name: true } });
    if (!product) {
      return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${productId} missing for return line.`)], diagnostics: ["RETURN_PRODUCT_MISSING"], touchedModels: ["SaleReturn", "SaleReturnLine", "Product"] };
    }
    const saleLine = sale?.lines?.find((candidate: any) => candidate.id === asString(line.saleLineId) || candidate.productId === productId) ?? null;
    returnLinePlans.push({ index, line, product, productId, qty, saleLine });
  }

  if (!returnLinePlans.length) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "sale.refunded lines must include productId and qty.", "rejected")], diagnostics: ["RETURN_LINES_INVALID"], touchedModels: ["SaleReturn", "SaleReturnLine"] };
  }

  await tx.saleReturn.create({
    data: {
      id: returnId,
      businessId: event.businessId,
      saleFolio,
      reason: asString(payload.reasonLabel ?? payload.reason) || "Devolucion sincronizada",
      amountCents,
      status: asString(payload.status) || "CREATED",
      cashier: asString(payload.cashier) || event.actorId,
      createdAt: asDate(payload.createdAt, event.occurredAt)
    }
  });

  const touchedModels = ["SaleReturn"];
  for (const { index, line, product, productId, qty, saleLine } of returnLinePlans) {
    const restoreStock = asBool(line.restoreStock, true);
    let stockMovementId: string | null = null;
    if (restoreStock) {
      stockMovementId = `${event.eventId}_return_stock_${index + 1}`;
      const existingMovement = await tx.stockMovement.findUnique({ where: { id: stockMovementId } }).catch(() => null);
      if (!existingMovement) {
        await tx.stockMovement.create({
          data: {
            id: stockMovementId,
            businessId: event.businessId,
            productId,
            movement: "RETURN",
            qty,
            reason: "sale.refunded",
            location: asString(payload.location) || "tablet-floor",
            createdAt: asDate(payload.createdAt, event.occurredAt)
          }
        });
        await tx.product.update({ where: { id: productId }, data: { stockOnHand: { increment: qty } } });
      }
      if (!touchedModels.includes("StockMovement")) touchedModels.push("StockMovement");
      if (!touchedModels.includes("Product")) touchedModels.push("Product");
    }
    await tx.saleReturnLine.create({
      data: {
        id: asString(line.id) || `${event.eventId}_return_line_${index + 1}`,
        businessId: event.businessId,
        saleReturnId: returnId,
        saleId: sale?.id ?? asOptionalString(payload.saleId),
        saleLineId: saleLine?.id ?? asOptionalString(line.saleLineId),
        productId,
        sku: asString(line.sku) || product.sku,
        productName: asString(line.productName ?? line.name) || product.name,
        qty,
        amountCents: lineAmountCents(line, qty),
        restoreStock,
        stockMovementId,
        createdAt: asDate(payload.createdAt, event.occurredAt)
      }
    });
    if (!touchedModels.includes("SaleReturnLine")) touchedModels.push("SaleReturnLine");
  }
  return { status: "projected", conflicts: [], diagnostics: ["SALE_REFUND_PROJECTED_WITH_LINES"], touchedModels };
}

async function projectSaleCancelled(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const payload = event.payload;
  const saleId = asString(payload.saleId) || event.aggregateId;
  if (!saleId) return { status: "dead_letter", conflicts: [conflict("invalid_schema", "sale.cancelled requires saleId.", "rejected")], diagnostics: ["SALE_CANCEL_PAYLOAD_INCOMPLETE"], touchedModels: ["Sale"] };
  const sale = await tx.sale.findFirst({ where: { id: saleId, businessId: event.businessId }, include: { lines: true } });
  if (!sale) return { status: "recognized_not_projected", conflicts: [], diagnostics: ["SALE_CANCEL_WAITING_FOR_SALE"], touchedModels: ["OutboxEvent"] };
  if (sale.status === "CANCELLED") return { status: "reconciled", conflicts: [], diagnostics: ["SALE_ALREADY_CANCELLED"], touchedModels: ["Sale"] };
  await tx.sale.update({ where: { id: saleId }, data: { status: "CANCELLED" } });
  const touchedModels = ["Sale"];
  if (asBool(payload.restoreStock, false)) {
    for (const [index, line] of sale.lines.entries()) {
      const movementId = `${event.eventId}_cancel_stock_${index + 1}`;
      await tx.stockMovement.create({
        data: {
          id: movementId,
          businessId: event.businessId,
          productId: line.productId,
          movement: "CANCEL_RESTORE",
          qty: line.qty,
          reason: "sale.cancelled",
          location: asString(payload.location) || "tablet-floor",
          createdAt: asDate(payload.createdAt, event.occurredAt)
        }
      }).catch(() => null);
      await tx.product.update({ where: { id: line.productId }, data: { stockOnHand: { increment: line.qty } } });
    }
    touchedModels.push("StockMovement", "Product");
  }
  return { status: "projected", conflicts: [], diagnostics: ["SALE_CANCELLED_PROJECTED"], touchedModels };
}


function supplierPayload(event: SyncEventEnvelope) {
  const payload = event.payload;
  const after = asRecord(payload.after);
  const source = Object.keys(after).length ? after : payload;
  const supplierId = asString(source.supplierId ?? source.id ?? payload.supplierId) || event.aggregateId;
  return {
    supplierId,
    name: asString(source.name ?? source.tradeName ?? payload.name ?? payload.tradeName),
    status: asString(source.status ?? payload.status) || (event.topic === "supplier.disabled" ? "DISABLED" : "ACTIVE"),
    createdAt: source.createdAt ?? payload.createdAt,
    updatedAt: source.updatedAt ?? payload.updatedAt
  };
}

async function projectSupplier(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["SUPPLIER_PRECONDITION_FAILED"], touchedModels: ["Supplier"] };

  const data = supplierPayload(event);
  if (!data.supplierId) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "supplier.* requires supplierId.", "rejected")], diagnostics: ["SUPPLIER_PAYLOAD_INCOMPLETE"], touchedModels: ["Supplier"] };
  }
  if (event.topic !== "supplier.disabled" && !data.name) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "supplier.created/updated require name.", "rejected")], diagnostics: ["SUPPLIER_NAME_MISSING"], touchedModels: ["Supplier"] };
  }

  const existing = await tx.supplier.findFirst({ where: { id: data.supplierId, businessId: event.businessId } });
  const nextName = data.name || existing?.name || data.supplierId;
  const byName = await tx.supplier.findUnique({ where: { businessId_name: { businessId: event.businessId, name: nextName } } }).catch(() => null);
  if (byName && byName.id !== data.supplierId) {
    return { status: "conflict", conflicts: [conflict("duplicate_event", `Supplier name ${nextName} already belongs to supplier ${byName.id}.`)], diagnostics: ["SUPPLIER_NAME_COLLISION"], touchedModels: ["Supplier"] };
  }

  await tx.supplier.upsert({
    where: { id: data.supplierId },
    create: {
      id: data.supplierId,
      businessId: event.businessId,
      name: nextName,
      status: data.status,
      createdAt: asDate(data.createdAt, event.occurredAt)
    },
    update: {
      name: nextName,
      status: data.status,
      updatedAt: asDate(data.updatedAt, event.occurredAt)
    }
  });
  return { status: existing ? "reconciled" : "projected", conflicts: [], diagnostics: [existing ? "SUPPLIER_UPDATED" : "SUPPLIER_CREATED"], touchedModels: ["Supplier"] };
}

function productSupplierPayload(event: SyncEventEnvelope) {
  const payload = event.payload;
  const after = asRecord(payload.after);
  const source = Object.keys(after).length ? after : payload;
  const productId = asString(source.productId ?? payload.productId);
  const supplierId = asString(source.supplierId ?? payload.supplierId);
  const linkId = asString(source.productSupplierId ?? source.linkId ?? source.id ?? payload.productSupplierId ?? payload.linkId) || event.aggregateId || (productId && supplierId ? `${productId}_${supplierId}` : "");
  return {
    linkId,
    productId,
    supplierId,
    isPrimary: asBool(source.isPrimary ?? payload.isPrimary, false),
    status: asString(source.status ?? payload.status) || (event.topic === "product.supplier.unlinked" ? "INACTIVE" : "ACTIVE"),
    leadTimeDays: asInt(source.leadTimeDays ?? payload.leadTimeDays),
    createdAt: source.createdAt ?? payload.createdAt,
    updatedAt: source.updatedAt ?? payload.updatedAt
  };
}

async function projectProductSupplier(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  const baseConflicts = await ensureBusinessAndTerminal(tx, event);
  if (baseConflicts.length) return { status: "conflict", conflicts: baseConflicts, diagnostics: ["PRODUCT_SUPPLIER_PRECONDITION_FAILED"], touchedModels: ["ProductSupplier"] };

  const data = productSupplierPayload(event);
  if (!data.productId || !data.supplierId) {
    return { status: "dead_letter", conflicts: [conflict("invalid_schema", "product.supplier.* requires productId and supplierId.", "rejected")], diagnostics: ["PRODUCT_SUPPLIER_PAYLOAD_INCOMPLETE"], touchedModels: ["ProductSupplier"] };
  }
  const [product, supplier] = await Promise.all([
    tx.product.findFirst({ where: { id: data.productId, businessId: event.businessId }, select: { id: true } }),
    tx.supplier.findFirst({ where: { id: data.supplierId, businessId: event.businessId }, select: { id: true } })
  ]);
  if (!product) return { status: "conflict", conflicts: [conflict("product_discontinued", `Product ${data.productId} missing for supplier link.`)], diagnostics: ["PRODUCT_SUPPLIER_PRODUCT_MISSING"], touchedModels: ["Product", "ProductSupplier"] };
  if (!supplier) return { status: "conflict", conflicts: [conflict("inconsistent_sequence", `Supplier ${data.supplierId} missing for product link.`)], diagnostics: ["PRODUCT_SUPPLIER_SUPPLIER_MISSING"], touchedModels: ["Supplier", "ProductSupplier"] };

  const existing = await tx.productSupplier.findFirst({ where: { businessId: event.businessId, productId: data.productId, supplierId: data.supplierId } });
  const rowId = existing?.id || data.linkId || `${data.productId}_${data.supplierId}`.slice(0, 120);
  if (event.topic === "product.supplier.unlinked") {
    if (!existing) return { status: "reconciled", conflicts: [], diagnostics: ["PRODUCT_SUPPLIER_ALREADY_UNLINKED"], touchedModels: ["ProductSupplier"] };
    await tx.productSupplier.update({ where: { id: existing.id }, data: { status: "INACTIVE", isPrimary: false, updatedAt: asDate(data.updatedAt, event.occurredAt) } });
    return { status: "reconciled", conflicts: [], diagnostics: ["PRODUCT_SUPPLIER_UNLINKED"], touchedModels: ["ProductSupplier"] };
  }

  if (data.isPrimary) {
    await tx.productSupplier.updateMany({ where: { businessId: event.businessId, productId: data.productId, NOT: { id: rowId } }, data: { isPrimary: false } });
  }
  await tx.productSupplier.upsert({
    where: { id: rowId },
    create: {
      id: rowId,
      businessId: event.businessId,
      productId: data.productId,
      supplierId: data.supplierId,
      isPrimary: data.isPrimary,
      status: data.status,
      leadTimeDays: data.leadTimeDays,
      createdAt: asDate(data.createdAt, event.occurredAt)
    },
    update: {
      isPrimary: data.isPrimary,
      status: data.status,
      leadTimeDays: data.leadTimeDays,
      updatedAt: asDate(data.updatedAt, event.occurredAt)
    }
  });
  return { status: existing ? "reconciled" : "projected", conflicts: [], diagnostics: [existing ? "PRODUCT_SUPPLIER_UPDATED" : "PRODUCT_SUPPLIER_LINKED"], touchedModels: ["ProductSupplier", "Product", "Supplier"] };
}

export async function projectAcceptedSyncEvent(tx: TxClient, event: SyncEventEnvelope): Promise<SyncProjectionResult> {
  if (event.topic === "sale.created") return projectSaleCreated(tx, event);
  if (event.topic === "customer.created") return projectCustomerCreated(tx, event);
  if (event.topic === "sale.completed") return projectSaleCompleted(tx, event);
  if (event.topic === "ticket.closed") return projectTicketClosed(tx, event);
  if (event.topic === "stock.decremented") return projectStockDecremented(tx, event);
  if (event.topic === "stock.adjusted") return projectStockAdjusted(tx, event);
  if (event.topic === "inventory.operation.recorded") return projectInventoryOperationRecorded(tx, event);
  if (event.topic === "cash.session.opened" || event.topic === "shift.opened") return projectCashSessionOpened(tx, event);
  if (event.topic === "cash.movement.recorded" || event.topic === "shift.closed") return projectCashMovementRecorded(tx, event);
  if (event.topic === "inventory.low_stock_detected") return projectLowStockDetected(tx, event);
  if (event.topic === "catalog.product.created" || event.topic === "catalog.product.updated") return projectCatalogProduct(tx, event);
  if (event.topic === "sale.refunded") return projectSaleRefunded(tx, event);
  if (event.topic === "sale.cancelled") return projectSaleCancelled(tx, event);
  if (event.topic === "supplier.created" || event.topic === "supplier.updated" || event.topic === "supplier.disabled") return projectSupplier(tx, event);
  if (event.topic === "product.supplier.linked" || event.topic === "product.supplier.unlinked" || event.topic === "product.supplier.updated") return projectProductSupplier(tx, event);
  return unsupported(event);
}
