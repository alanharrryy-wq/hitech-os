import { prisma } from "../prisma/client";import { OUTBOX_STATUS_PENDING, POS_EVENT_CASH_MOVEMENT_RECORDED, POS_EVENT_CASH_SESSION_OPENED, POS_EVENT_SCHEMA_VERSION, POS_EVENT_SOURCE } from "../pos-engine/constants";import { makePosId } from "../pos-engine/ids";import type { CloseShiftInput, OpenShiftInput, ShiftCashSummary } from "./types";import { SHIFT_STATUS_CLOSED, SHIFT_STATUS_OPEN, ShiftError } from "./types";
type TxClient=any;const OPENING_FLOAT="OPENING_FLOAT";const CLOSING_COUNT="CLOSING_COUNT";const SHIFT_OPENED_TOPIC=POS_EVENT_CASH_SESSION_OPENED;const SHIFT_CLOSED_TOPIC=POS_EVENT_CASH_MOVEMENT_RECORDED;
async function persistShiftEvent(tx:TxClient,topic:string,session:any,payload:Record<string,unknown>){const occurredAt=new Date();const eventId=makePosId("evt");const event={eventId,eventType:topic,topic,idempotencyKey:`${topic}:${session.businessId}:${session.terminalId}:${session.id}:${payload.movement??"cash-session"}`,businessId:session.businessId,terminalId:session.terminalId,actorId:session.cashierId,source:POS_EVENT_SOURCE,occurredAt:occurredAt.toISOString(),aggregateId:session.id,schemaVersion:POS_EVENT_SCHEMA_VERSION,correlationId:session.id,payload};await tx.outboxEvent.create({data:{id:event.eventId,businessId:session.businessId,topic,aggregateId:session.id,idempotencyKey:event.idempotencyKey,terminalId:event.terminalId,source:event.source,schemaVersion:event.schemaVersion,payloadJson:JSON.stringify(event),status:OUTBOX_STATUS_PENDING,createdAt:occurredAt}});}
async function ensureTerminal(tx:TxClient,businessId:string,terminalId:string){const terminal=await tx.terminal.findFirst({where:{id:terminalId,businessId,isActive:true}});if(!terminal)throw new ShiftError("TERMINAL_NOT_FOUND","No hay terminal local activa para operar caja.",409,{businessId,terminalId});return terminal;}
async function buildSummary(tx:TxClient,session:any):Promise<ShiftCashSummary>{const[sales,movements]=await Promise.all([tx.sale.findMany({where:{businessId:session.businessId,cashSessionId:session.id,status:"COMPLETED"}}),tx.cashMovement.findMany({where:{businessId:session.businessId,cashSessionId:session.id},orderBy:{createdAt:"asc"}})]);const salesTotalCents=sales.reduce((sum:number,sale:any)=>sum+sale.totalCents,0);const operationalMovementCents=movements.filter((m:any)=>m.movement!==OPENING_FLOAT&&m.movement!==CLOSING_COUNT).reduce((sum:number,m:any)=>sum+m.amountCents,0);const expectedCashCents=session.expectedCashCents??session.cashStartCents+salesTotalCents+operationalMovementCents;const varianceCents=session.varianceCents??(session.cashEndCents===null||session.cashEndCents===undefined?null:session.cashEndCents-expectedCashCents);const isOpen=session.status===SHIFT_STATUS_OPEN;return{id:session.id,businessId:session.businessId,storeId:session.storeId,terminalId:session.terminalId,cashierId:session.cashierId,cashier:session.cashier,status:session.status,openedAt:session.openedAt.toISOString(),closedAt:session.closedAt?session.closedAt.toISOString():null,cashStartCents:session.cashStartCents,cashEndCents:session.cashEndCents??null,expectedCashCents,varianceCents,salesCount:sales.length,salesTotalCents,movementCount:movements.length,canSell:isOpen,canClose:isOpen,operatorMessage:isOpen?"Turno abierto. Las ventas nuevas se ligan a esta caja.":"Turno cerrado. Abre uno nuevo para volver a vender."};}
export class PrismaShiftCashRepository {
  private readonly db: any;

  constructor(db = prisma) {
    this.db = db;
  }

  async current(input: { businessId: string; terminalId: string }): Promise<ShiftCashSummary | null> {
    const session = await this.db.cashSession.findFirst({
      where: { businessId: input.businessId, terminalId: input.terminalId, status: SHIFT_STATUS_OPEN },
      orderBy: { openedAt: "desc" }
    });
    return session ? buildSummary(this.db, session) : null;
  }

  async open(input: OpenShiftInput): Promise<ShiftCashSummary> {
    return this.db.$transaction(async (tx: TxClient) => {
      const terminal = await ensureTerminal(tx, input.businessId, input.terminalId);
      const existing = await tx.cashSession.findFirst({
        where: { businessId: input.businessId, terminalId: input.terminalId, status: SHIFT_STATUS_OPEN }
      });
      if (existing) throw new ShiftError("SHIFT_ALREADY_OPEN", "Ya hay un turno abierto en esta terminal.", 409, { shiftId: existing.id });

      const now = new Date();
      const session = await tx.cashSession.create({
        data: {
          id: makePosId("shift"),
          businessId: input.businessId,
          storeId: terminal.storeId,
          terminalId: input.terminalId,
          cashierId: input.cashierId,
          cashier: input.cashier,
          openedAt: now,
          cashStartCents: input.cashStartCents,
          status: SHIFT_STATUS_OPEN
        }
      });
      await tx.cashMovement.create({
        data: {
          id: makePosId("cash_move"),
          businessId: input.businessId,
          cashSessionId: session.id,
          movement: OPENING_FLOAT,
          amountCents: input.cashStartCents,
          reason: "Caja inicial registrada al abrir turno.",
          createdAt: now
        }
      });
      await persistShiftEvent(tx, SHIFT_OPENED_TOPIC, session, {
        cashSessionId: session.id,
        cashStartCents: input.cashStartCents,
        cashier: input.cashier,
        movement: OPENING_FLOAT,
        amountCents: input.cashStartCents,
        openedAt: now.toISOString()
      });
      return buildSummary(tx, session);
    });
  }

  async close(input: CloseShiftInput): Promise<ShiftCashSummary> {
    return this.db.$transaction(async (tx: TxClient) => {
      const session = await tx.cashSession.findFirst({
        where: { businessId: input.businessId, terminalId: input.terminalId, status: SHIFT_STATUS_OPEN },
        orderBy: { openedAt: "desc" }
      });
      if (!session) throw new ShiftError("SHIFT_NOT_OPEN", "No hay turno abierto para cerrar caja.", 409, { businessId: input.businessId, terminalId: input.terminalId });

      const before = await buildSummary(tx, session);
      const varianceCents = input.countedCashCents - before.expectedCashCents;
      const now = new Date();
      const updated = await tx.cashSession.update({
        where: { id: session.id },
        data: {
          closedAt: now,
          cashEndCents: input.countedCashCents,
          expectedCashCents: before.expectedCashCents,
          varianceCents,
          status: SHIFT_STATUS_CLOSED
        }
      });
      await tx.cashMovement.create({
        data: {
          id: makePosId("cash_move"),
          businessId: input.businessId,
          cashSessionId: session.id,
          movement: CLOSING_COUNT,
          amountCents: input.countedCashCents,
          reason: input.note ? `Conteo de cierre: ${input.note}` : "Conteo de cierre de turno.",
          createdAt: now
        }
      });
      await persistShiftEvent(tx, SHIFT_CLOSED_TOPIC, updated, {
        cashSessionId: updated.id,
        movement: CLOSING_COUNT,
        amountCents: input.countedCashCents,
        countedCashCents: input.countedCashCents,
        expectedCashCents: before.expectedCashCents,
        varianceCents,
        salesCount: before.salesCount,
        salesTotalCents: before.salesTotalCents,
        closedAt: now.toISOString()
      });
      return buildSummary(tx, updated);
    });
  }
}
export const shiftCashRepository=new PrismaShiftCashRepository();
