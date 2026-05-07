import { prisma } from "@/server/prisma/client";
import {
  REQUIRED_SYNC_EVENT_FIELDS,
  getSyncConflictCatalog
} from "@/server/validators/sync-event-contract";
import type { SyncReleaseWorkspace } from "@/modules/sync/types";

function labelDate(value: Date | string | null | undefined) {
  if (!value) return "No disponible";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function isoDate(value: Date | string | null | undefined) {
  if (!value) return new Date(0).toISOString();
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? new Date(0).toISOString() : date.toISOString();
}

export function buildSyncDryRunSample() {
  const base = new Date().toISOString();
  return {
    events: [
      {
        eventId: "dry_run_sale_completed_001",
        topic: "sale.completed",
        businessId: "business_demo",
        terminalId: "tablet_01",
        actorId: "operator_demo",
        source: "tablet",
        occurredAt: base,
        schemaVersion: "1.0.0",
        payload: { saleId: "sale_demo_001", totalCents: 12900, stockAfter: 8, terminalRegistered: true }
      },
      {
        eventId: "dry_run_sale_completed_001",
        topic: "sale.completed",
        businessId: "business_demo",
        terminalId: "tablet_01",
        actorId: "operator_demo",
        source: "tablet",
        occurredAt: base,
        schemaVersion: "1.0.0",
        payload: { saleId: "sale_demo_001", totalCents: 12900, stockAfter: 8, terminalRegistered: true }
      },
      {
        eventId: "dry_run_stock_conflict_001",
        topic: "stock.decremented",
        businessId: "business_demo",
        terminalId: "tablet_01",
        actorId: "operator_demo",
        source: "tablet",
        occurredAt: base,
        schemaVersion: "1.0.0",
        payload: { productId: "sku_demo", stockAfter: -2, localPriceCents: 1000, currentPriceCents: 1200 }
      }
    ]
  };
}

export async function getSyncReleaseWorkspace(): Promise<SyncReleaseWorkspace> {
  const generatedAt = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date());
  const statusModel = [
    { status: "accepted", description: "Evento válido y persistible." },
    { status: "duplicate", description: "eventId repetido o ya persistido." },
    { status: "conflict", description: "Evento válido con conflicto operativo." },
    { status: "rejected", description: "Evento inválido por contrato." }
  ];

  try {
    const db = prisma as any;
    const [totalEvents, ackedEvents, conflictEvents, failedEvents, recentRows] = await Promise.all([
      db.outboxEvent.count(),
      db.outboxEvent.count({ where: { status: "acked" } }),
      db.outboxEvent.count({ where: { status: "conflict" } }),
      db.outboxEvent.count({ where: { status: "failed" } }),
      db.outboxEvent.findMany({ orderBy: { createdAt: "desc" }, take: 12 })
    ]);
    return {
      summary: { totalEvents, ackedEvents, conflictEvents, failedEvents },
      requiredFields: [...REQUIRED_SYNC_EVENT_FIELDS],
      statusModel,
      conflictCatalog: getSyncConflictCatalog(),
      recentEvents: recentRows.map((row: any) => ({
        id: row.id,
        topic: row.topic,
        status: row.status,
        aggregateId: row.aggregateId,
        createdAt: isoDate(row.createdAt),
        createdAtLabel: labelDate(row.createdAt)
      })),
      sampleDryRunPayload: buildSyncDryRunSample(),
      meta: { persistence: "available", confidence: "real", generatedAt, warnings: [] }
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Error desconocido leyendo OutboxEvent.";
    return {
      summary: { totalEvents: null, ackedEvents: null, conflictEvents: null, failedEvents: null },
      requiredFields: [...REQUIRED_SYNC_EVENT_FIELDS],
      statusModel,
      conflictCatalog: getSyncConflictCatalog(),
      recentEvents: [],
      sampleDryRunPayload: buildSyncDryRunSample(),
      meta: { persistence: "unavailable", confidence: "blocked", generatedAt, warnings: ["No se pudo cargar la información. Revisa la sincronización o la base local."] }
    };
  }
}
