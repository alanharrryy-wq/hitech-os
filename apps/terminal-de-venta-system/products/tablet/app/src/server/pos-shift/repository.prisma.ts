import crypto from "node:crypto";
import { prisma } from "../prisma/client";
import {
  OUTBOX_STATUS_PENDING,
  POS_EVENT_SCHEMA_VERSION,
  POS_EVENT_SOURCE
} from "../pos-engine/constants";
import { makePosId } from "../pos-engine/ids";
import { assertTabletOperationalPermission } from "../pos-security/permissions.prisma";
import type { CloseShiftInput, OpenShiftInput, RecordCashMovementInput, RecordCashMovementResult, ShiftCashSummary } from "./types";
import { SHIFT_STATUS_CLOSED, SHIFT_STATUS_OPEN, ShiftError } from "./types";

type TxClient = any;

const OPENING_FLOAT = "OPENING_FLOAT";
const CLOSING_COUNT = "CLOSING_COUNT";
const POS_EVENT_CASH_SESSION_OPENED = "cash.session.opened";
const POS_EVENT_CASH_MOVEMENT_RECORDED = "cash.movement.recorded";
const POS_EVENT_VERSION = "1.0.0";

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (!value || typeof value !== "object") return value;
  return Object.keys(value as Record<string, unknown>).sort().reduce<Record<string, unknown>>((acc, key) => {
    acc[key] = stable((value as Record<string, unknown>)[key]);
    return acc;
  }, {});
}

function payloadHash(value: unknown) {
  return crypto.createHash("sha256").update(JSON.stringify(stable(value))).digest("hex");
}

function sequenceFor(at: Date, eventId: string) {
  const suffix = [...eventId].reduce((sum, char) => (sum + char.charCodeAt(0)) % 1000, 0);
  return at.getTime() * 1000 + suffix;
}

async function persistShiftEvent(
  tx: TxClient,
  topic: string,
  session: any,
  payload: Record<string, unknown>
) {
  const occurredAt = new Date();
  const eventId = makePosId("evt");
  const tenantId = process.env.PRISMA_TENANT_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TENANT_ID?.trim() || "";
  const customerId = process.env.PRISMA_CUSTOMER_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_CUSTOMER_ID?.trim() || "";
  const deviceId = process.env.PRISMA_TABLET_DEVICE_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_DEVICE_ID?.trim() || session.terminalId;
  const originRecordId = String(payload.cashMovementId ?? payload.cashSessionId ?? session.id);
  const correlationId = session.id;
  const event = {
    eventId,
    source: POS_EVENT_SOURCE,
    subject: `prisma://sync/${encodeURIComponent(tenantId || "unresolved-tenant")}/${encodeURIComponent(session.businessId)}/${encodeURIComponent(session.storeId)}/${encodeURIComponent(session.terminalId)}/${encodeURIComponent(deviceId)}/${encodeURIComponent(topic)}/${encodeURIComponent(session.id)}`,
    eventType: topic,
    topic,
    eventVersion: POS_EVENT_VERSION,
    schemaVersion: POS_EVENT_SCHEMA_VERSION,
    tenantId,
    ...(customerId ? { customerId } : {}),
    businessId: session.businessId,
    storeId: session.storeId,
    terminalId: session.terminalId,
    deviceId,
    actorId: session.cashierId,
    aggregateId: session.id,
    originRecordId,
    idempotencyKey: `${topic}:${session.businessId}:${session.terminalId}:${session.id}:${payload.clientRequestId ?? payload.movement ?? "cash-session"}`,
    sequence: sequenceFor(occurredAt, eventId),
    correlationId,
    causationId: correlationId,
    traceId: correlationId,
    occurredAt: occurredAt.toISOString(),
    capturedAt: occurredAt.toISOString(),
    payloadHash: payloadHash(payload),
    payload
  };

  await tx.outboxEvent.create({
    data: {
      id: event.eventId,
      businessId: session.businessId,
      topic,
      aggregateId: session.id,
      idempotencyKey: event.idempotencyKey,
      terminalId: event.terminalId,
      source: event.source,
      schemaVersion: event.schemaVersion,
      payloadJson: JSON.stringify(event),
      status: OUTBOX_STATUS_PENDING,
      createdAt: occurredAt
    }
  });
}

async function ensureTerminal(tx: TxClient, businessId: string, terminalId: string) {
  const terminal = await tx.terminal.findFirst({
    where: { id: terminalId, businessId, isActive: true }
  });
  if (!terminal) {
    throw new ShiftError(
      "TERMINAL_NOT_FOUND",
      "No hay terminal local activa para operar caja.",
      409,
      { businessId, terminalId }
    );
  }
  return terminal;
}

async function buildSummary(tx: TxClient, session: any): Promise<ShiftCashSummary> {
  const [sales, movements] = await Promise.all([
    tx.sale.findMany({
      where: {
        businessId: session.businessId,
        cashSessionId: session.id,
        status: "COMPLETED"
      }
    }),
    tx.cashMovement.findMany({
      where: {
        businessId: session.businessId,
        cashSessionId: session.id
      },
      orderBy: { createdAt: "asc" }
    })
  ]);
  const salesTotalCents = sales.reduce((sum: number, sale: any) => sum + sale.totalCents, 0);
  const operationalMovementCents = movements
    .filter((movement: any) => movement.movement !== OPENING_FLOAT && movement.movement !== CLOSING_COUNT)
    .reduce((sum: number, movement: any) => sum + movement.amountCents, 0);
  const expectedCashCents = session.expectedCashCents ?? session.cashStartCents + salesTotalCents + operationalMovementCents;
  const varianceCents = session.varianceCents ?? (
    session.cashEndCents === null || session.cashEndCents === undefined
      ? null
      : session.cashEndCents - expectedCashCents
  );
  const isOpen = session.status === SHIFT_STATUS_OPEN;
  return {
    id: session.id,
    businessId: session.businessId,
    storeId: session.storeId,
    terminalId: session.terminalId,
    cashierId: session.cashierId,
    cashier: session.cashier,
    status: session.status,
    openedAt: session.openedAt.toISOString(),
    closedAt: session.closedAt ? session.closedAt.toISOString() : null,
    cashStartCents: session.cashStartCents,
    cashEndCents: session.cashEndCents ?? null,
    expectedCashCents,
    varianceCents,
    salesCount: sales.length,
    salesTotalCents,
    movementCount: movements.length,
    canSell: isOpen,
    canClose: isOpen,
    operatorMessage: isOpen
      ? "Turno abierto. Las ventas nuevas se ligan a esta caja."
      : "Turno cerrado. Abre uno nuevo para volver a vender."
  };
}

export class PrismaShiftCashRepository {
  private readonly db: any;

  constructor(db = prisma) {
    this.db = db;
  }

  async current(input: { businessId: string; terminalId: string }): Promise<ShiftCashSummary | null> {
    const session = await this.db.cashSession.findFirst({
      where: {
        businessId: input.businessId,
        terminalId: input.terminalId,
        status: SHIFT_STATUS_OPEN
      },
      orderBy: { openedAt: "desc" }
    });
    return session ? buildSummary(this.db, session) : null;
  }

  async recentMovements(input: { businessId: string; terminalId: string }) {
    const session = await this.db.cashSession.findFirst({
      where: { businessId: input.businessId, terminalId: input.terminalId, status: SHIFT_STATUS_OPEN },
      orderBy: { openedAt: "desc" }
    });
    if (!session) return [];
    return this.db.cashMovement.findMany({
      where: { businessId: input.businessId, cashSessionId: session.id, movement: { in: ["CASH_IN", "CASH_OUT"] } },
      orderBy: { createdAt: "desc" },
      take: 12
    });
  }

  async recordMovement(input: RecordCashMovementInput): Promise<RecordCashMovementResult> {
    return this.db.$transaction(async (tx: TxClient) => {
      const session = await tx.cashSession.findFirst({
        where: { businessId: input.businessId, terminalId: input.terminalId, status: SHIFT_STATUS_OPEN },
        orderBy: { openedAt: "desc" }
      });
      if (!session) throw new ShiftError("SHIFT_NOT_OPEN", "Abre turno antes de registrar movimientos de caja.", 409, { businessId: input.businessId, terminalId: input.terminalId });
      if (input.actorId !== session.cashierId) {
        throw new ShiftError("CASH_ACTOR_MISMATCH", "El responsable debe ser el cajero del turno abierto.", 403, { actorId: input.actorId, cashierId: session.cashierId });
      }
      const permission = await assertTabletOperationalPermission({
        businessId: input.businessId,
        terminalId: input.terminalId,
        actorId: input.actorId,
        permission: "cash:adjust"
      }, tx);

      const idempotencyKey = `${POS_EVENT_CASH_MOVEMENT_RECORDED}:${session.businessId}:${session.terminalId}:${session.id}:${input.clientRequestId}`;
      const existingEvent = await tx.outboxEvent.findFirst({ where: { businessId: input.businessId, idempotencyKey } });
      if (existingEvent) {
        const envelope = JSON.parse(existingEvent.payloadJson || "{}") as { payload?: { cashMovementId?: string; adjustmentId?: string } };
        const movementId = envelope.payload?.cashMovementId;
        const existingMovement = movementId ? await tx.cashMovement.findFirst({ where: { id: movementId, businessId: input.businessId } }) : null;
        if (!existingMovement) throw new ShiftError("CASH_IDEMPOTENCY_INCONSISTENT", "El evento idempotente existe sin movimiento de caja asociado.", 409, { idempotencyKey });
        return {
          movement: {
            id: existingMovement.id,
            cashSessionId: existingMovement.cashSessionId,
            movement: existingMovement.movement,
            amountCents: existingMovement.amountCents,
            reason: existingMovement.reason,
            createdAt: existingMovement.createdAt.toISOString(),
            adjustmentId: envelope.payload?.adjustmentId ?? null,
            actorId: input.actorId,
            clientRequestId: input.clientRequestId,
            deduplicated: true
          },
          shift: await buildSummary(tx, session)
        };
      }

      const createdAt = new Date();
      const signedAmountCents = input.movement === "CASH_OUT" ? -Math.abs(input.amountCents) : Math.abs(input.amountCents);
      const movement = await tx.cashMovement.create({
        data: {
          id: makePosId("cash_move"),
          businessId: input.businessId,
          cashSessionId: session.id,
          movement: input.movement,
          amountCents: signedAmountCents,
          reason: input.reason,
          createdAt
        }
      });
      const actor = await tx.user.findFirst({ where: { id: input.actorId, businessId: input.businessId, status: "ACTIVE" }, select: { id: true } });
      const adjustment = await tx.cashAdjustment.create({
        data: {
          id: makePosId("cash_adjust"),
          businessId: input.businessId,
          cashSessionId: session.id,
          cashMovementId: movement.id,
          actorId: actor?.id ?? null,
          adjustmentType: input.movement,
          amountCents: signedAmountCents,
          reason: input.reason,
          evidenceJson: JSON.stringify({ contract: "PRISMA_TABLET_CASH_MOVEMENT_V1", clientRequestId: input.clientRequestId, actorId: input.actorId }),
          createdAt
        }
      });
      await tx.auditEvent.create({
        data: {
          id: makePosId("audit"),
          businessId: input.businessId,
          actorId: actor?.id ?? null,
          topic: "cash.movement.recorded",
          entityType: "cash_movement",
          entityId: movement.id,
          summary: input.movement === "CASH_IN" ? "Entrada manual de caja registrada." : "Salida manual de caja registrada.",
          afterJson: JSON.stringify({ movement: input.movement, amountCents: signedAmountCents, reason: input.reason }),
          metadataJson: JSON.stringify({ clientRequestId: input.clientRequestId, cashSessionId: session.id, terminalId: session.terminalId, actorId: input.actorId, permission: permission.permission, authorizationMode: permission.authorizationMode }),
          createdAt
        }
      });
      await persistShiftEvent(tx, POS_EVENT_CASH_MOVEMENT_RECORDED, session, {
        cashSessionId: session.id,
        cashMovementId: movement.id,
        adjustmentId: adjustment.id,
        movement: input.movement,
        amountCents: signedAmountCents,
        reason: input.reason,
        actorId: input.actorId,
        permission: permission.permission,
        authorizationMode: permission.authorizationMode,
        clientRequestId: input.clientRequestId,
        createdAt: createdAt.toISOString()
      });
      return {
        movement: {
          id: movement.id,
          cashSessionId: session.id,
          movement: input.movement,
          amountCents: signedAmountCents,
          reason: input.reason,
          createdAt: createdAt.toISOString(),
          adjustmentId: adjustment.id,
          actorId: input.actorId,
          clientRequestId: input.clientRequestId,
          deduplicated: false
        },
        shift: await buildSummary(tx, session)
      };
    });
  }

  async open(input: OpenShiftInput): Promise<ShiftCashSummary> {
    return this.db.$transaction(async (tx: TxClient) => {
      const terminal = await ensureTerminal(tx, input.businessId, input.terminalId);
      const existing = await tx.cashSession.findFirst({
        where: {
          businessId: input.businessId,
          terminalId: input.terminalId,
          status: SHIFT_STATUS_OPEN
        }
      });
      if (existing) {
        throw new ShiftError(
          "SHIFT_ALREADY_OPEN",
          "Ya hay un turno abierto en esta terminal.",
          409,
          { shiftId: existing.id }
        );
      }

      const openedAt = new Date();
      const session = await tx.cashSession.create({
        data: {
          id: makePosId("shift"),
          businessId: input.businessId,
          storeId: terminal.storeId,
          terminalId: input.terminalId,
          cashierId: input.cashierId,
          cashier: input.cashier,
          openedAt,
          cashStartCents: input.cashStartCents,
          status: SHIFT_STATUS_OPEN
        }
      });
      const movement = await tx.cashMovement.create({
        data: {
          id: makePosId("cash_move"),
          businessId: input.businessId,
          cashSessionId: session.id,
          movement: OPENING_FLOAT,
          amountCents: input.cashStartCents,
          reason: "Caja inicial registrada al abrir turno.",
          createdAt: openedAt
        }
      });

      await persistShiftEvent(tx, POS_EVENT_CASH_SESSION_OPENED, session, {
        cashSessionId: session.id,
        cashMovementId: movement.id,
        cashStartCents: input.cashStartCents,
        cashier: input.cashier,
        movement: OPENING_FLOAT,
        amountCents: input.cashStartCents,
        openedAt: openedAt.toISOString()
      });
      return buildSummary(tx, session);
    });
  }

  async close(input: CloseShiftInput): Promise<ShiftCashSummary> {
    return this.db.$transaction(async (tx: TxClient) => {
      const session = await tx.cashSession.findFirst({
        where: {
          businessId: input.businessId,
          terminalId: input.terminalId,
          status: SHIFT_STATUS_OPEN
        },
        orderBy: { openedAt: "desc" }
      });
      if (!session) {
        throw new ShiftError(
          "SHIFT_NOT_OPEN",
          "No hay turno abierto para cerrar caja.",
          409,
          { businessId: input.businessId, terminalId: input.terminalId }
        );
      }

      const before = await buildSummary(tx, session);
      const varianceCents = input.countedCashCents - before.expectedCashCents;
      const closedAt = new Date();
      const updated = await tx.cashSession.update({
        where: { id: session.id },
        data: {
          closedAt,
          cashEndCents: input.countedCashCents,
          expectedCashCents: before.expectedCashCents,
          varianceCents,
          status: SHIFT_STATUS_CLOSED
        }
      });
      const movement = await tx.cashMovement.create({
        data: {
          id: makePosId("cash_move"),
          businessId: input.businessId,
          cashSessionId: session.id,
          movement: CLOSING_COUNT,
          amountCents: input.countedCashCents,
          reason: input.note
            ? `Conteo de cierre: ${input.note}`
            : "Conteo de cierre de turno.",
          createdAt: closedAt
        }
      });

      await persistShiftEvent(tx, POS_EVENT_CASH_MOVEMENT_RECORDED, updated, {
        cashSessionId: updated.id,
        cashMovementId: movement.id,
        movement: CLOSING_COUNT,
        amountCents: input.countedCashCents,
        countedCashCents: input.countedCashCents,
        expectedCashCents: before.expectedCashCents,
        varianceCents,
        salesCount: before.salesCount,
        salesTotalCents: before.salesTotalCents,
        closedAt: closedAt.toISOString(),
        closesSession: true
      });
      return buildSummary(tx, updated);
    });
  }
}

export const shiftCashRepository = new PrismaShiftCashRepository();
