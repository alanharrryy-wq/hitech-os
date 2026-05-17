-- PRISMA event-ledger lifecycle extension.
-- Forward-only, additive columns for PC ingest/projector governance.

ALTER TABLE "OutboxEvent" ADD COLUMN "terminalId" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "eventType" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "idempotencyKey" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "correlationId" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "source" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "schemaVersion" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "lifecycleStatus" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "receivedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "validatedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "acceptedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "projectedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "reconciledAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "failedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "deadLetterAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "conflictCode" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "diagnosticsJson" TEXT;

CREATE INDEX "idx_outboxevent_business_lifecycle_created"
  ON "OutboxEvent"("businessId", "lifecycleStatus", "createdAt");

CREATE INDEX "idx_outboxevent_business_idempotency"
  ON "OutboxEvent"("businessId", "idempotencyKey");
